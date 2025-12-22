<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { itemApi } from '$lib/api';
    import { goto } from '$app/navigation';

    let item: any = null;
    let loading = true;
    let error = '';
    let activeImageIndex = 0;

    onMount(async () => {
        const token = localStorage.getItem('token');
        if (!token) {
            goto('/login');
            return;
        }
        
        const id = $page.params.id ?? '';
        try {
            item = await itemApi.getOne(id);
        } catch (err: any) {
            error = err.message;
        } finally {
            loading = false;
        }
    });

    function goBack() {
        goto('/items');
    }

    async function handleAddToWishlist() {
        if (!item) return;
        try {
            await itemApi.addToWishlist(item.item_id);
            alert('❤️ 已加入收藏！');
        } catch (err: any) {
            alert('加入失敗：' + err.message);
        }
    }
</script>

<div class="min-h-screen bg-gray-50 p-4 md:p-12">
    <div class="max-w-5xl mx-auto">
        <button on:click={goBack} class="mb-8 flex items-center text-gray-500 hover:text-blue-600 transition-colors font-medium">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clip-rule="evenodd" />
            </svg>
            返回列表
        </button>

        {#if loading}
            <div class="flex justify-center items-center h-64">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        {:else if error}
            <div class="bg-red-50 text-red-600 p-6 rounded-2xl text-center font-medium border border-red-100">
                {error}
            </div>
        {:else if item}
            <div class="bg-white rounded-[2.5rem] shadow-xl overflow-hidden border border-gray-100">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-0">
                    <!-- 圖片區域 -->
                    <div class="bg-gray-100 p-8 flex flex-col items-center justify-center relative min-h-[400px]">
                        {#if item.images && item.images.length > 0}
                            <img 
                                src={`http://localhost:8000${item.images[activeImageIndex]}`} 
                                alt={item.title}
                                class="w-full h-full object-contain max-h-[500px] rounded-xl shadow-sm"
                            />
                            
                            {#if item.images.length > 1}
                                <div class="absolute bottom-6 flex space-x-2">
                                    {#each item.images as _, i}
                                        <button 
                                            class="w-3 h-3 rounded-full transition-all {i === activeImageIndex ? 'bg-blue-600 scale-125' : 'bg-gray-300 hover:bg-gray-400'}"
                                            on:click={() => activeImageIndex = i}
                                            aria-label="Select image {i + 1}"
                                        ></button>
                                    {/each}
                                </div>
                            {/if}
                        {:else}
                            <div class="text-gray-400 flex flex-col items-center">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-20 w-20 mb-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                </svg>
                                <span class="font-medium">暫無圖片</span>
                            </div>
                        {/if}
                    </div>

                    <!-- 資訊區域 -->
                    <div class="p-10 md:p-12 flex flex-col">
                        <div class="flex items-center space-x-3 mb-6">
                            <span class="px-4 py-1.5 bg-blue-50 text-blue-700 text-sm font-bold rounded-full border border-blue-100">
                                {item.condition}
                            </span>
                            <span class="px-4 py-1.5 bg-purple-50 text-purple-700 text-sm font-bold rounded-full border border-purple-100">
                                {item.exchange_type ? '交換' : '出售'}
                            </span>
                            <span class="text-gray-400 text-sm font-medium ml-auto">
                                {new Date(item.post_date).toLocaleDateString()}
                            </span>
                        </div>

                        <h1 class="text-4xl font-black text-gray-900 mb-4 leading-tight">{item.title}</h1>
                        
                        <div class="text-3xl font-bold text-blue-600 mb-8 flex items-baseline">
                            {#if !item.exchange_type}
                                <span class="text-lg mr-1 text-blue-400">$</span>{item.price}
                            {:else}
                                <span class="text-xl">想換：{item.desired_item || '任何等值物品'}</span>
                            {/if}
                        </div>

                        <div class="prose prose-blue max-w-none mb-10 text-gray-600 leading-relaxed">
                            <h3 class="text-lg font-bold text-gray-900 mb-2">商品描述</h3>
                            <p>{item.description || '賣家未提供詳細描述'}</p>
                        </div>

                        <div class="mt-auto pt-8 border-t border-gray-100">
                            <div class="flex items-center justify-between mb-6">
                                <div class="flex items-center">
                                    <div class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-500 font-bold mr-3">
                                        U
                                    </div>
                                    <div>
                                        <p class="text-sm text-gray-500">賣家</p>
                                        <p class="font-bold text-gray-900">User #{item.owner_id}</p>
                                    </div>
                                </div>
                            </div>

                            <div class="flex space-x-4">
                                <button on:click={handleAddToWishlist} class="flex-1 py-4 bg-pink-50 text-pink-600 rounded-2xl font-bold text-lg border border-pink-100 hover:bg-pink-100 transition-all">
                                    加入收藏
                                </button>
                                <button class="flex-[2] py-4 bg-blue-600 text-white rounded-2xl font-bold text-lg shadow-lg shadow-blue-200 hover:bg-blue-700 hover:shadow-xl hover:-translate-y-0.5 transition-all active:translate-y-0">
                                    聯絡賣家
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        {/if}
    </div>
</div>
