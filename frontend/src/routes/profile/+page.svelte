<script lang="ts">
    import { onMount } from 'svelte';
    import { userApi } from '$lib/api';
    import { goto } from '$app/navigation';

    let user: any = null;
    let loading = true;
    let error = '';

    onMount(async () => {
        const token = localStorage.getItem('token');
        if (!token) {
            goto('/login');
            return;
        }
        await loadProfile();
    });

    async function loadProfile() {
        try {
            loading = true;
            user = await userApi.getProfile();
        } catch (err: any) {
            error = err.message;
        } finally {
            loading = false;
        }
    }

    function logout() {
        localStorage.removeItem('token');
        goto('/login');
    }
</script>

<div class="min-h-screen bg-gray-50 p-4 md:p-12">
    <div class="max-w-3xl mx-auto">
        <div class="flex items-center justify-between mb-10">
            <div class="flex items-center">
                <button on:click={() => goto('/items')} class="mr-6 p-2 rounded-full hover:bg-gray-200 transition-colors" aria-label="Go to items">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                    </svg>
                </button>
                <h1 class="text-4xl font-black text-gray-900 tracking-tight">個人檔案</h1>
            </div>
            <button on:click={logout} class="px-6 py-2 bg-white border border-gray-200 text-red-600 rounded-2xl font-bold hover:bg-red-50 hover:border-red-100 transition-all shadow-sm">
                登出
            </button>
        </div>

        {#if loading}
            <div class="flex justify-center items-center h-64">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        {:else if error}
            <div class="bg-red-50 text-red-600 p-6 rounded-2xl text-center font-medium border border-red-100">
                {error}
            </div>
        {:else if user}
            <div class="bg-white rounded-[2.5rem] shadow-xl overflow-hidden border border-gray-100 p-10">
                <div class="flex items-center mb-10">
                    <div class="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 text-3xl font-black mr-8">
                        {user.username.charAt(0).toUpperCase()}
                    </div>
                    <div>
                        <h2 class="text-3xl font-black text-gray-900">{user.username}</h2>
                        <p class="text-gray-500 font-medium">加入時間：{new Date(user.join_date).toLocaleDateString()}</p>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div class="bg-gray-50 p-6 rounded-3xl">
                        <h3 class="text-sm font-bold text-gray-400 uppercase tracking-wider mb-2">Email</h3>
                        <p class="text-lg font-bold text-gray-800">{user.email}</p>
                    </div>

                    <div class="bg-gray-50 p-6 rounded-3xl">
                        <h3 class="text-sm font-bold text-gray-400 uppercase tracking-wider mb-2">地址</h3>
                        <p class="text-lg font-bold text-gray-800">{user.address || '未設定'}</p>
                    </div>

                    <div class="bg-gray-50 p-6 rounded-3xl md:col-span-2">
                        <h3 class="text-sm font-bold text-gray-400 uppercase tracking-wider mb-2">聯絡電話</h3>
                        {#if user.phones && user.phones.length > 0}
                            <div class="flex flex-wrap gap-3">
                                {#each user.phones as phone}
                                    <span class="px-4 py-2 bg-white rounded-xl font-bold text-gray-700 shadow-sm border border-gray-100">
                                        {phone}
                                    </span>
                                {/each}
                            </div>
                        {:else}
                            <p class="text-gray-400 italic">未設定電話</p>
                        {/if}
                    </div>
                </div>
                
                <div class="mt-10 pt-10 border-t border-gray-100 flex justify-end">
                    <button on:click={() => goto('/wishlist')} class="flex items-center px-8 py-4 bg-pink-50 text-pink-600 rounded-2xl font-bold hover:bg-pink-100 transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd" />
                        </svg>
                        查看我的收藏
                    </button>
                </div>
            </div>
        {/if}
    </div>
</div>
