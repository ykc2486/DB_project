<script lang="ts">
	import { onMount } from 'svelte';
	import { itemApi } from '$lib/api'; // 修正後的路徑
	import { goto } from '$app/navigation';

	let items: any[] = [];
	let loading = true;
	let error = '';

	onMount(async () => {
		const token = localStorage.getItem('token');
		if (!token || token === 'undefined') {
			goto('/login');
			return;
		}
		try {
			items = await itemApi.getAll();
		} catch (err: any) {
			error = err.message;
		} finally {
			loading = false;
		}
	});

	function logout() {
		localStorage.removeItem('token');
		goto('/login');
	}
</script>

<div class="p-8 max-w-4xl mx-auto">
	<div class="flex justify-between items-center mb-8 border-b pb-4">
		<h1 class="text-3xl font-bold text-gray-800">二手交易市集</h1>
		<button on:click={logout} class="bg-gray-100 px-4 py-2 rounded-lg hover:bg-red-50 hover:text-red-600 transition font-medium">登出系統</button>
	</div>

	{#if loading}
		<div class="text-center py-20">載入中...</div>
	{:else if error}
		<div class="bg-red-50 text-red-600 p-4 rounded-xl border border-red-100">{error}</div>
	{:else if items.length === 0}
		<div class="text-center py-20 bg-gray-50 rounded-2xl border-2 border-dashed">
			<p class="text-gray-400">目前市集上沒有任何商品。</p>
		</div>
	{:else}
		<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
			{#each items as item}
				<div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
					<h3 class="text-xl font-bold mb-2">{item.title}</h3>
					<p class="text-gray-500 text-sm mb-4 line-clamp-2">{item.description || '無描述'}</p>
					<div class="flex justify-between items-center pt-4 border-t">
						<span class="text-green-600 font-black text-xl">NT$ {item.price}</span>
						<span class="text-xs text-gray-400">{item.condition}</span>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>