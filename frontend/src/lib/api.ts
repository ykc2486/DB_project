// src/lib/api.ts
// 1. 導入環境變數
import { PUBLIC_BACKEND_URL } from '$env/static/public';

// 2. 將硬編碼網址替換為變數
const BASE_URL = PUBLIC_BACKEND_URL;
export const getFullImageUrl = (imagePath: string) => {
    if (!imagePath) return '';

    const ROOT_URL = PUBLIC_BACKEND_URL.replace(/\/api$/, '');


    if (imagePath.startsWith('/api')) {
        return `${ROOT_URL}${imagePath}`;
    }

    return `${BASE_URL}${imagePath}`;
};

export const authApi = {
    async register(userData: any) {
        const response = await fetch(`${BASE_URL}/users/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData),
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '註冊失敗');
        }
        return response.json();
    },

    async login(loginData: any) {
        // 1. 強制轉換：如果收到的是 FormData，將其轉為純物件
        let payload = loginData;
        if (loginData instanceof FormData) {
            payload = Object.fromEntries(loginData.entries());
        }

        console.log("🚀 API 準備發送的 JSON 字串:", JSON.stringify(payload));

        const response = await fetch(`${BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            // 2. 確保 body 絕對不是空的大括號
            body: JSON.stringify({
                username: payload.username,
                password: payload.password
            }),
        });

        if (!response.ok) {
            const error = await response.json();
            const msg = Array.isArray(error.detail)
                ? error.detail.map((e: any) => `${e.loc[e.loc.length - 1]}: ${e.msg}`).join(' | ')
                : error.detail;
            throw new Error(msg || '帳號或密碼錯誤');
        }
        return response.json();
    }
};

export const itemApi = {
    async getAll(search = '', sort = '') {
        const token = localStorage.getItem('token');
        // 構建 Query String
        const params = new URLSearchParams();
        if (search) params.append('search', search);
        if (sort) params.append('sort', sort);

        const url = `${BASE_URL}/items/?${params.toString()}`;

        const response = await fetch(url, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('無法取得商品');
        return response.json();
    },

    async create(formData: FormData) {
        const token = localStorage.getItem('token');
        // 關鍵：同樣走 ?token= 模式，確保後端 verify_token 抓得到
        const response = await fetch(`${BASE_URL}/items/?token=${token}`, {
            method: 'POST',
            body: formData
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '上架失敗');
        }
        return response.json();
    },

    async getOne(id: string) {
        const token = localStorage.getItem('token');
        const response = await fetch(`${BASE_URL}/items/${id}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('無法取得商品詳情');
        return response.json();
    },

    async addToWishlist(itemId: number) {
        const token = localStorage.getItem('token');
        const response = await fetch(`${BASE_URL}/wishlist/?token=${token}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_id: itemId })
        });
        if (!response.ok) throw new Error('加入收藏失敗');
        return response.json();
    },

    async getWishlist() {
        const token = localStorage.getItem('token');
        const response = await fetch(`${BASE_URL}/wishlist/?token=${token}`);
        if (!response.ok) throw new Error('無法取得收藏清單');
        return response.json();
    },

    async update(id: number, itemData: any) {
        const token = localStorage.getItem('token');
        const response = await fetch(`${BASE_URL}/items/${id}?token=${token}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(itemData)
        });
        if (!response.ok) throw new Error('更新商品失敗');
        return response.json();
    },

    async delete(id: number) {
        const token = localStorage.getItem('token');
        const response = await fetch(`${BASE_URL}/items/${id}?token=${token}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('刪除商品失敗');
        return response.json();
    }
};

export const userApi = {
    async getProfile() {
        const token = localStorage.getItem('token');
        const response = await fetch(`${BASE_URL}/users/me?token=${token}`);
        if (!response.ok) throw new Error('無法取得使用者資料');
        return response.json();
    },
    // --- 新增更新方法 ---
    async updateProfile(profileData: any) {
        const token = localStorage.getItem('token');
        const response = await fetch(`${BASE_URL}/users/me?token=${token}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(profileData)
        });
        if (!response.ok) throw new Error('更新個人檔案失敗');
        return response.json();
    },

    async read_user_by_id(id: number) {
        const token = localStorage.getItem('token');
        const response = await fetch(`${BASE_URL}/users/${id}?token=${token}`);
        if (!response.ok) throw new Error('無法取得該用戶資料');
        return response.json();
    }
};

export const transactionApi = {
    async create(itemId: number) {
        const token = localStorage.getItem('token');
        const response = await fetch(`${BASE_URL}/transactions/?token=${token}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_id: itemId })
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '交易建立失敗');
        }
        return response.json();
    },

    async getAll() {
        const token = localStorage.getItem('token');
        const response = await fetch(`${BASE_URL}/transactions/?token=${token}`);
        if (!response.ok) throw new Error('無法取得交易紀錄');
        return response.json();
    },

    async updateStatus(transactionId: number, status: string) {
        const token = localStorage.getItem('token');
        const response = await fetch(`${BASE_URL}/transactions/${transactionId}?token=${token}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status })
        });
        if (!response.ok) throw new Error('更新狀態失敗');
        return response.json();
    },

    async delete(id: number) {
        const token = localStorage.getItem('token');
        const response = await fetch(`${BASE_URL}/transactions/${id}?token=${token}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('刪除紀錄失敗');
        return response.json();
    }
};

export const messageApi = {
    async send(receiverId: number, content: string, itemId: number) {
        const token = localStorage.getItem('token');
        const response = await fetch(`${BASE_URL}/messages/?token=${token}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ receiver_id: receiverId, content, item_id: itemId })
        });
        if (!response.ok) throw new Error('訊息發送失敗');
        return response.json();
    },

    // 修正：增加 itemId 參數，並傳遞給後端
    async getHistory(otherUserId: number, itemId: number) {
        const token = localStorage.getItem('token');
        const response = await fetch(`${BASE_URL}/messages/${otherUserId}?token=${token}&item_id=${itemId}`);
        if (!response.ok) throw new Error('無法取得訊息紀錄');
        return response.json();
    },

    async getConversations() {
        const token = localStorage.getItem('token');
        const response = await fetch(`${BASE_URL}/conversations/?token=${token}`);
        if (!response.ok) throw new Error('無法取得對話列表');
        return response.json();
    }
};
