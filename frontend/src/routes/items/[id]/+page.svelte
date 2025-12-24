<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { itemApi, transactionApi, userApi } from '$lib/api'; // 確保導入 userApi
	import { goto } from '$app/navigation';
	import {getFullImageUrl} from '$lib/api';

	let item: any = null;
	let loading = true;
	let error = '';
	let activeImageIndex = 0;
	let currentUserId: number | null = null; // 新增：追蹤目前登入者的 ID

	onMount(async () => {
		const token = localStorage.getItem('token');
		if (!token) {
			goto('/login');
			return;
		}

		const id = $page.params.id ?? '';
		try {
			// 同時取得商品資訊與目前的個人檔案
			const [itemData, userData] = await Promise.all([itemApi.getOne(id), userApi.getProfile()]);

			item = itemData;
			currentUserId = userData.user_id; // 取得當前使用者 ID
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

	async function handleTransaction() {
		if (!item) return;
		if (!confirm('確定要發起交易嗎？')) return;
		try {
			await transactionApi.create(item.item_id);
			alert('交易請求已發送！');
			goto('/transactions');
		} catch (err: any) {
			alert('交易失敗：' + err.message);
		}
	}

	// 修正：傳訊息改為「賣家ID_商品ID」格式，並防止給自己傳訊息
	function handleContact() {
		if (!item) return;
		goto(`/messages/${item.owner_id}_${item.item_id}`);
	}

	function viewSellerProfile() {
		if (!item) return;
		goto(`/users/${item.owner_id}`);
	}
</script>

<div class="min-h-screen bg-gray-50 p-4 md:p-12">
	<div class="mx-auto max-w-5xl">
		<button
			on:click={goBack}
			class="mb-8 flex items-center font-medium text-gray-500 transition-colors hover:text-blue-600"
		>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				class="mr-2 h-5 w-5"
				viewBox="0 0 20 20"
				fill="currentColor"
			>
				<path
					fill-rule="evenodd"
					d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z"
					clip-rule="evenodd"
				/>
			</svg>
			返回列表
		</button>

		{#if loading}
			<div class="flex h-64 items-center justify-center">
				<div class="h-12 w-12 animate-spin rounded-full border-b-2 border-blue-600"></div>
			</div>
		{:else if error}
			<div
				class="rounded-2xl border border-red-100 bg-red-50 p-6 text-center font-medium text-red-600"
			>
				{error}
			</div>
		{:else if item}
			<div class="overflow-hidden rounded-[2.5rem] border border-gray-100 bg-white shadow-xl">
				<div class="grid grid-cols-1 gap-0 md:grid-cols-2">
					<div
						class="relative flex min-h-[400px] flex-col items-center justify-center bg-gray-100 p-8"
					>
						{#if item.images && item.images.length > 0}
							<img
								src={`${getFullImageUrl(item.images[activeImageIndex])}`}
								alt={item.title}
								class="h-full max-h-[500px] w-full rounded-xl object-contain shadow-sm"
							/>
							{#if item.images.length > 1}
								<div class="absolute bottom-6 flex space-x-2">
									{#each item.images as _, i}
										<button
											class="h-3 w-3 rounded-full transition-all {i === activeImageIndex
												? 'scale-125 bg-blue-600'
												: 'bg-gray-300 hover:bg-gray-400'}"
											on:click={() => (activeImageIndex = i)}
											aria-label="Select image {i + 1}"
										></button>
									{/each}
								</div>
							{/if}
						{:else}
							<div class="flex flex-col items-center text-gray-400">
								<svg
									xmlns="http://www.w3.org/2000/svg"
									class="mb-4 h-20 w-20 opacity-50"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="1.5"
										d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
									/>
								</svg>
								<span class="font-medium">暫無圖片</span>
							</div>
						{/if}
					</div>

					<div class="flex flex-col p-10 md:p-12">
						<div class="mb-6 flex items-center space-x-3">
							<span
								class="rounded-full border border-blue-100 bg-blue-50 px-4 py-1.5 text-sm font-bold text-blue-700"
							>
								{item.condition}
							</span>
							<span
								class="rounded-full border border-purple-100 bg-purple-50 px-4 py-1.5 text-sm font-bold text-purple-700"
							>
								{item.exchange_type ? '交換' : '出售'}
							</span>
							<span class="ml-auto text-sm font-medium text-gray-400">
								{new Date(item.post_date).toLocaleDateString()}
							</span>
						</div>

						<h1 class="mb-4 text-4xl leading-tight font-black text-gray-900">{item.title}</h1>

						<div class="mb-8 flex items-baseline text-3xl font-bold text-blue-600">
							{#if !item.exchange_type}
								<span class="mr-1 text-lg text-blue-400">$</span>{item.price}
							{:else}
								<span class="text-xl">想換：{item.desired_item || '任何等值物品'}</span>
							{/if}
						</div>

						<div class="prose prose-blue mb-10 max-w-none leading-relaxed text-gray-600">
							<h3 class="mb-2 text-lg font-bold text-gray-900">商品描述</h3>
							<p>{item.description || '賣家未提供詳細描述'}</p>
						</div>

						<div class="mt-auto border-t border-gray-100 pt-8">
							<div class="mb-6 flex items-center justify-between">
								<button
									on:click={viewSellerProfile}
									class="flex items-center rounded-xl p-2 text-left transition-colors hover:bg-gray-50"
								>
									<div
										class="mr-3 flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 font-bold text-white shadow-sm"
									>
										{item.owner_id}
									</div>
									<div>
										<p class="text-sm text-gray-500">
											{item.owner_id === currentUserId ? '這是您的商品' : '賣家'}
										</p>
										<p class="font-bold text-gray-900">
											User #{item.owner_id}
											<span class="ml-1 text-xs font-medium text-blue-500">查看檔案</span>
										</p>
									</div>
								</button>
							</div>

							<div class="flex space-x-4">
								{#if item.owner_id === currentUserId}
									<button
										on:click={() => goto('/items')}
										class="flex-1 rounded-2xl bg-gray-900 py-4 text-center text-lg font-bold text-white shadow-lg transition-all hover:bg-gray-800"
									>
										返回市集管理
									</button>
								{:else}
									<button
										on:click={handleAddToWishlist}
										class="flex-1 rounded-2xl border border-pink-100 bg-pink-50 py-4 text-lg font-bold text-pink-600 transition-all hover:bg-pink-100"
									>
										加入收藏
									</button>
									<button
										on:click={handleContact}
										class="flex-1 rounded-2xl border border-gray-200 bg-gray-100 py-4 text-lg font-bold text-gray-700 transition-all hover:bg-gray-200"
									>
										聯絡賣家
									</button>
									<button
										on:click={handleTransaction}
										class="flex-[2] rounded-2xl bg-blue-600 py-4 text-lg font-bold text-white shadow-lg shadow-blue-200 transition-all hover:-translate-y-0.5 hover:bg-blue-700 hover:shadow-xl active:translate-y-0"
									>
										{item.exchange_type ? '提出交換' : '立即購買'}
									</button>
								{/if}
							</div>
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>
</div>
