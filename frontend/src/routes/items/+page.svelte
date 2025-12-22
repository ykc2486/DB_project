<script lang="ts">
    import { onMount } from 'svelte';
    import { itemApi } from '$lib/api';
    import { goto } from '$app/navigation';

    // 狀態變數
    let items: any[] = [];
    let loading = true;
    let error = '';

    // 上架表單變數
    let title = '';
    let description = '';
    let price: number | null = null;
    let condition = '良好';
    let category = 1;
    let exchangeType = false; // false = 出售, true = 交換
    let desiredItem = '';
    let files: FileList | null = null;
    let uploadLoading = false;

    onMount(async () => {
        const token = localStorage.getItem('token');
        if (!token || token === 'undefined') {
            goto('/login');
            return;
        }
        await loadItems();
    });

    async function loadItems() {
        try {
            loading = true;
            error = ''; // 重置錯誤
            items = await itemApi.getAll();
        } catch (err: any) {
            error = err.message;
        } finally {
            loading = false;
        }
    }

    async function handleCreate() {
        if (!title) {
            alert('請填寫商品名稱');
            return;
        }
        if (!exchangeType && (price === null || price < 0)) {
            alert('出售商品請填寫有效價格');
            return;
        }
        
        uploadLoading = true;
        const formData = new FormData();
        formData.append('title', title);
        formData.append('description', description);
        formData.append('condition', condition);
        formData.append('category', category.toString());
        formData.append('exchange_type', exchangeType.toString());
        
        if (exchangeType) {
            formData.append('desired_item', desiredItem);
            formData.append('price', '0'); // 交換模式下價格設為 0
        } else {
            formData.append('price', price?.toString() || '0');
        }

        if (files) {
            for (let i = 0; i < files.length; i++) {
                formData.append('images', files[i]);
            }
        }

        try {
            await itemApi.create(formData);
            alert('✨ 商品上架成功！');
            // 清空表單
            title = ''; description = ''; price = null; desiredItem = ''; files = null;
            exchangeType = false;
            await loadItems(); // 重新整理列表
        } catch (err: any) {
            alert('上架失敗：' + err.message);
        } finally {
            uploadLoading = false;
        }
    }

    function logout() {
        localStorage.removeItem('token');
        goto('/login');
    }
</script>

<div class="min-h-screen bg-gray-50 p-4 md:p-12">
    <div class="max-w-7xl mx-auto flex justify-between items-center mb-10">
        <div>
            <h1 class="text-4xl font-black text-gray-900 tracking-tight">二手交易市集</h1>
            <p class="text-gray-500 mt-1">找到你心儀的寶物，或是賦予舊愛新生命。</p>
        </div>
        <button on:click={logout} class="px-6 py-2 bg-white border border-gray-200 text-gray-600 rounded-2xl font-bold hover:bg-red-50 hover:text-red-600 hover:border-red-100 transition-all shadow-sm">
            登出系統
        </button>
    </div>

    <div class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-12">
        
        <div class="lg:col-span-4">
            <div class="bg-white p-8 rounded-[2rem] shadow-xl border border-gray-100 sticky top-12">
                <div class="flex items-center mb-8">
                    <div class="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-white mr-4 shadow-lg shadow-blue-200">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                        </svg>
                    </div>
                    <h2 class="text-2xl font-black text-gray-800">我要上架</h2>
                </div>

                <div class="space-y-5">
                    <div>
                        <label for="title" class="block text-sm font-bold text-gray-700 mb-2">商品名稱</label>
                        <input id="title" bind:value={title} placeholder="你想賣什麼？" class="w-full border-gray-200 border p-4 rounded-2xl bg-gray-50 focus:bg-white focus:ring-4 focus:ring-blue-50 outline-none transition-all" />
                    </div>

                    <div>
                        <label for="transaction-type" class="block text-sm font-bold text-gray-700 mb-2">交易方式</label>
                        <div id="transaction-type" class="flex space-x-4">
                            <button 
                                class="flex-1 py-3 rounded-xl font-bold border-2 transition-all {exchangeType === false ? 'border-blue-600 bg-blue-50 text-blue-700' : 'border-gray-200 text-gray-500 hover:border-gray-300'}"
                                on:click={() => exchangeType = false}
                            >
                                💰 出售
                            </button>
                            <button 
                                class="flex-1 py-3 rounded-xl font-bold border-2 transition-all {exchangeType === true ? 'border-purple-600 bg-purple-50 text-purple-700' : 'border-gray-200 text-gray-500 hover:border-gray-300'}"
                                on:click={() => exchangeType = true}
                            >
                                🔄 交換
                            </button>
                        </div>
                    </div>

                    {#if !exchangeType}
                        <div>
                            <label for="price" class="block text-sm font-bold text-gray-700 mb-2">售價 (NT$)</label>
                            <input id="price" type="number" bind:value={price} placeholder="0" class="w-full border-gray-200 border p-4 rounded-2xl bg-gray-50 focus:bg-white focus:ring-4 focus:ring-blue-50 outline-none transition-all font-mono font-bold text-blue-600" />
                        </div>
                    {:else}
                        <div>
                            <label for="desiredItem" class="block text-sm font-bold text-gray-700 mb-2">想換什麼？</label>
                            <input id="desiredItem" bind:value={desiredItem} placeholder="例如：PS5 遊戲片、二手相機..." class="w-full border-gray-200 border p-4 rounded-2xl bg-gray-50 focus:bg-white focus:ring-4 focus:ring-purple-50 outline-none transition-all" />
                        </div>
                    {/if}

                    <div>
                        <label for="description" class="block text-sm font-bold text-gray-700 mb-2">商品描述</label>
                        <textarea id="description" bind:value={description} rows="4" placeholder="描述一下商品的新舊程度、使用狀況..." class="w-full border-gray-200 border p-4 rounded-2xl bg-gray-50 focus:bg-white focus:ring-4 focus:ring-blue-50 outline-none transition-all resize-none"></textarea>
                    </div>

                    <div>
                        <label for="condition-select" class="block text-sm font-bold text-gray-700 mb-2">物品狀況</label>
                        <select id="condition-select" bind:value={condition} class="w-full border-gray-200 border p-4 rounded-2xl bg-gray-50 focus:bg-white outline-none appearance-none cursor-pointer">
                            <option>全新</option><option>良好</option><option>普通</option><option>損壞</option>
                        </select>
                    </div>

                    <div>
                        <label for="product-images" class="block text-sm font-bold text-gray-700 mb-2">商品照片</label>
                        <div class="border-2 border-dashed border-gray-200 rounded-2xl p-6 text-center hover:border-blue-400 transition-colors">
                            <input id="product-images" type="file" multiple on:change={(e) => files = e.currentTarget.files} class="w-full text-xs text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer" />
                        </div>
                    </div>
                    
                    <button on:click={handleCreate} disabled={uploadLoading} class="w-full bg-blue-600 hover:bg-blue-700 text-white py-5 rounded-2xl font-black text-lg transition-all shadow-lg shadow-blue-200 disabled:bg-gray-300">
                        {uploadLoading ? '處理中...' : '確認發佈商品'}
                    </button>
                </div>
            </div>
        </div>

        <div class="lg:col-span-8">
            <h2 class="text-2xl font-black text-gray-800 mb-8 flex items-center">
                <span class="w-2 h-8 bg-emerald-500 rounded-full mr-3"></span>
                熱門商品
            </h2>

            {#if loading}
                <div class="flex flex-col items-center justify-center py-24">
                    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
                    <p class="text-gray-400 font-medium">正在為您搬運貨物...</p>
                </div>
            {:else if error}
                <div class="bg-red-50 text-red-600 p-6 rounded-3xl border border-red-100 font-bold">⚠️ {error}</div>
            {:else if items.length === 0}
                <div class="text-center py-32 bg-white rounded-[2rem] border-2 border-dashed border-gray-200">
                    <p class="text-gray-400 text-lg">目前市集空空如也，快來當第一個賣家吧！</p>
                </div>
            {:else}
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {#each items as item}
                        <div class="group bg-white rounded-[2rem] shadow-sm hover:shadow-2xl transition-all duration-500 border border-gray-100 overflow-hidden flex flex-col">
                            <div class="h-56 bg-gray-100 relative overflow-hidden">
                                {#if item.images && item.images.length > 0}
                                    <img src={`http://localhost:8000${item.images[0]}`} class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" alt={item.title} />
                                {:else}
                                    <div class="w-full h-full flex items-center justify-center text-gray-300 italic bg-gray-50">No Image</div>
                                {/if}
                                <div class="absolute top-4 right-4 px-3 py-1 bg-white/90 backdrop-blur rounded-full text-[10px] font-black uppercase tracking-widest text-gray-500 shadow-sm">
                                    {item.condition}
                                </div>
                            </div>

                            <div class="p-8 flex-1">
                                <h3 class="text-2xl font-black text-gray-800 mb-3 group-hover:text-blue-600 transition-colors">{item.title}</h3>
                                <p class="text-gray-500 text-sm leading-relaxed line-clamp-2 mb-6">{item.description || '這件商品還沒有描述...'}</p>
                                
                                <div class="mt-auto flex justify-between items-center pt-6 border-t border-gray-50">
                                    <div class="flex flex-col">
                                        {#if !item.exchange_type}
                                            <span class="text-[10px] font-black text-gray-400 uppercase tracking-tighter mb-1">售價</span>
                                            <span class="text-3xl font-black text-emerald-600 tracking-tighter">
                                                <span class="text-sm font-bold mr-0.5">NT$</span>{item.price.toLocaleString()}
                                            </span>
                                        {:else}
                                            <span class="text-[10px] font-black text-purple-400 uppercase tracking-tighter mb-1">交換</span>
                                            <span class="text-xl font-black text-purple-600 tracking-tighter truncate max-w-[150px]">
                                                {item.desired_item || '任何物品'}
                                            </span>
                                        {/if}
                                    </div>
                                    <button on:click={() => goto(`/items/${item.item_id}`)} class="w-12 h-12 bg-gray-900 text-white rounded-2xl flex items-center justify-center hover:bg-blue-600 transition-all shadow-lg shadow-gray-200" aria-label="View item details">
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        </div>
                    {/each}
                </div>
            {/if}
        </div>
    </div>
</div>