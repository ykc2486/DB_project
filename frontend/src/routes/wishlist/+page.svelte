<script lang="ts">
    import { onMount } from 'svelte';
    import { itemApi } from '$lib/api';
    import { goto } from '$app/navigation';
    import { PUBLIC_BACKEND_URL } from '$env/static/public';
    import { getFullImageUrl } from '$lib/api';
    
    let wishlistItems: any[] = [];
    let loading = true;
    let error = '';

    onMount(async () => {
        const token = localStorage.getItem('token');
        if (!token) {
            goto('/login');
            return;
        }
        await loadWishlist();
    });

    async function loadWishlist() {
        try {
            loading = true;
            const res = await itemApi.getWishlist();
            // res is array of WishlistResponse, which has .item
            wishlistItems = res.map((w: any) => w.item).filter((i: any) => i !== null);
        } catch (err: any) {
            error = err.message;
        } finally {
            loading = false;
        }
    }
</script>

<div class="min-h-screen bg-gray-50 p-4 md:p-12">
    <div class="max-w-7xl mx-auto">
        <div class="flex items-center mb-10">
            <button on:click={() => goto('/items')} class="mr-6 p-2 rounded-full hover:bg-gray-200 transition-colors" aria-label="Go back to items">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
            </button>
            <div>
                <h1 class="text-4xl font-black text-gray-900 tracking-tight">我的收藏</h1>
                <p class="text-gray-500 mt-1">這裡是你關注的所有寶物。</p>
            </div>
        </div>

        {#if loading}
            <div class="flex justify-center items-center h-64">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-500"></div>
            </div>
        {:else if error}
            <div class="bg-red-50 text-red-600 p-6 rounded-2xl text-center font-medium border border-red-100">
                {error}
            </div>
        {:else if wishlistItems.length === 0}
            <div class="text-center py-32 bg-white rounded-[2rem] border-2 border-dashed border-gray-200">
                <div class="w-20 h-20 bg-pink-50 rounded-full flex items-center justify-center mx-auto mb-6 text-pink-400">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                </div>
                <p class="text-gray-500 text-lg font-medium">你的收藏清單還是空的</p>
                <button on:click={() => goto('/items')} class="mt-4 text-blue-600 font-bold hover:underline">去逛逛市集</button>
            </div>
        {:else}
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {#each wishlistItems as item}
                    <button type="button" class="group bg-white rounded-[2rem] shadow-sm hover:shadow-xl transition-all duration-300 border border-gray-100 overflow-hidden flex flex-col cursor-pointer" on:click={() => goto(`/items/${item.item_id}`)} aria-label={`View details for ${item.title}`}>
                        <div class="h-48 bg-gray-100 relative overflow-hidden">
                            {#if item.images && item.images.length > 0}
                                <img src={`${getFullImageUrl(item.images[0])}`} class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" alt={item.title} />
                            {:else}
                                <div class="w-full h-full flex items-center justify-center text-gray-300 italic bg-gray-50">No Image</div>
                            {/if}
                            <div class="absolute top-3 right-3 px-3 py-1 bg-white/90 backdrop-blur rounded-full text-[10px] font-black uppercase tracking-widest text-gray-500 shadow-sm">
                                {item.condition}
                            </div>
                        </div>

                        <div class="p-6 flex-1 flex flex-col">
                            <h3 class="text-xl font-bold text-gray-800 mb-2 group-hover:text-pink-600 transition-colors">{item.title}</h3>
                            
                            <div class="mt-auto pt-4 border-t border-gray-50 flex justify-between items-center">
                                {#if !item.exchange_type}
                                    <span class="text-2xl font-black text-gray-900">
                                        <span class="text-xs font-bold text-gray-400 mr-0.5">NT$</span>{item.price.toLocaleString()}
                                    </span>
                                {:else}
                                    <span class="text-lg font-black text-purple-600 truncate">
                                        交換: {item.desired_item || '任何物品'}
                                    </span>
                                {/if}
                            </div>
                        </div>
                    </button>
                {/each}
            </div>
        {/if}
    </div>
</div>
