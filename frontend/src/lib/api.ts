// src/lib/api.ts
const BASE_URL = 'http://localhost:8000/api';

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
                ? error.detail.map((e: any) => `${e.loc[e.loc.length-1]}: ${e.msg}`).join(' | ')
                : error.detail;
            throw new Error(msg || '帳號或密碼錯誤');
        }
        return response.json();
    }
};

export const itemApi = {
    async getAll() {
        const token = localStorage.getItem('token');
        const response = await fetch(`${BASE_URL}/items/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('無法取得商品');
        return response.json();
    }
};