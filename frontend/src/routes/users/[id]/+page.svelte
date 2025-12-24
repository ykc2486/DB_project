<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { userApi, itemApi } from '$lib/api';
	import { goto } from '$app/navigation';

	let seller: any = null;
	let sellerItems: any[] = [];
	let loading = true;
	let error = '';

	// 安全地解析 ID，避免產生 NaN
	const idParam = $page.params.id || '';
	const sellerId = parseInt(idParam);

	onMount(async () => {
		// 防禦性檢查：如果 ID 無效，不發送 API 請求
		if (!sellerId || isNaN(sellerId)) {
			error = '無效的使用者 ID。';
			loading = false;
			return;
		}

		try {
			loading = true;
			// 同時取得賣家資料與所有商品
			const [userData, allItems] = await Promise.all([
				userApi.read_user_by_id(sellerId),
				itemApi.getAll()
			]);

			seller = userData;
			// 從所有商品中過濾出屬於該賣家的
			sellerItems = allItems.filter((i: any) => i.owner_id === sellerId);
		} catch (err: any) {
			error = '載入賣家資訊失敗：' + err.message;
		} finally {
			loading = false;
		}
	});
</script>

<div class="min-h-screen bg-gray-50 p-4 md:p-12">
	<div class="mx-auto max-w-4xl">
		<button
			on:click={() => history.back()}
			class="mb-6 flex items-center font-bold text-gray-500 transition-colors hover:text-blue-600"
		>
			← 返回
		</button>

		{#if loading}
			<div class="flex flex-col items-center justify-center py-20">
				<div class="mb-4 h-12 w-12 animate-spin rounded-full border-b-2 border-blue-600"></div>
				<p class="text-gray-400">正在訪問賣場...</p>
			</div>
		{:else if error}
			<div
				class="rounded-[2rem] border border-red-100 bg-red-50 p-8 text-center font-bold text-red-600"
			>
				⚠️ {error}
			</div>
		{:else if seller}
			<div class="mb-12 rounded-[2.5rem] border border-gray-100 bg-white p-10 shadow-xl">
				<div class="mb-8 flex items-center">
					<div
						class="mr-8 flex h-24 w-24 items-center justify-center rounded-full bg-blue-100 text-4xl font-black text-blue-600 shadow-inner"
					>
						{seller.username.charAt(0).toUpperCase()}
					</div>
					<div>
						<h1 class="text-4xl font-black text-gray-900">{seller.username}</h1>
						<p class="font-medium text-gray-500">所在地：{seller.address || '未公開'}</p>
					</div>
				</div>

				<div class="grid grid-cols-2 gap-4">
					<div class="rounded-2xl bg-gray-50 p-6 text-center">
						<p class="mb-1 text-xs font-bold tracking-widest text-gray-400 uppercase">上架中</p>
						<p class="text-2xl font-black text-gray-800">
							{sellerItems.length} <span class="text-sm">件商品</span>
						</p>
					</div>
					<div class="rounded-2xl bg-gray-50 p-6 text-center">
						<p class="mb-1 text-xs font-bold tracking-widest text-gray-400 uppercase">加入時間</p>
						<p class="text-lg font-black text-gray-800">
							{new Date(seller.join_date).toLocaleDateString()}
						</p>
					</div>
				</div>
			</div>

			<h2 class="mb-8 flex items-center text-2xl font-black text-gray-800">
				<span class="mr-3 h-8 w-2 rounded-full bg-emerald-500"></span>
				{seller.username} 的商品
			</h2>

			{#if sellerItems.length === 0}
				<div
					class="rounded-[2rem] border-2 border-dashed border-gray-100 bg-white p-20 text-center"
				>
					<p class="text-gray-400 italic">目前沒有任何商品上架中。</p>
				</div>
			{:else}
				<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
					{#each sellerItems as item}
						<div
							class="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm transition-shadow hover:shadow-md"
						>
							<h3 class="mb-2 text-xl font-bold text-gray-800">{item.title}</h3>
							<p class="mb-6 line-clamp-2 text-sm text-gray-500">{item.description || '無描述'}</p>
							<div class="flex items-center justify-between border-t border-gray-50 pt-4">
								<span class="text-xl font-black text-blue-600">NT$ {item.price}</span>
								<button
									on:click={() => goto(`/items/${item.item_id}`)}
									class="text-sm font-bold text-blue-500 hover:underline">查看詳情</button
								>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		{/if}
	</div>
</div>
