<script lang="ts">
	import { onMount } from 'svelte';
	import { itemApi, userApi } from '$lib/api'; // 修正：導入 userApi 以取得目前使用者身份
	import { goto } from '$app/navigation';
	import { PUBLIC_BACKEND_URL } from '$env/static/public';
	import { getFullImageUrl } from '$lib/api';
	// 狀態變數
	let items: any[] = [];
	let loading = true;
	let error = '';
	let currentUserId: number | null = null; // 新增：存儲目前登入者的 ID

	// --- 額外功能狀態 (Search & Sort) ---
	let searchQuery = '';
	let sortOrder = 'newest';
	let searchTimeout: any;

	// --- 編輯狀態追蹤 ---
	let editingId: number | null = null;

	// 上架表單變數
	let title = '';
	let description = '';
	let price: number | null = null;
	let condition = '良好';
	let category = 1;
	let exchangeType = false;
	let desiredItem = '';
	let files: FileList | null = null;
	let uploadLoading = false;

	onMount(async () => {
		const token = localStorage.getItem('token');
		if (!token || token === 'undefined') {
			goto('/login');
			return;
		}
		await loadData(); // 修正：同時加載使用者與商品
	});

	async function loadData() {
		try {
			loading = true;
			error = '';
			// 同時取得商品與當前使用者資訊
			const [itemsData, userData] = await Promise.all([
				itemApi.getAll(searchQuery, sortOrder),
				userApi.getProfile()
			]);
			items = itemsData;
			currentUserId = userData.user_id; // 記錄目前使用者 ID
		} catch (err: any) {
			error = err.message;
		} finally {
			loading = false;
		}
	}

	async function loadItems() {
		try {
			// 單獨搜尋或排序時呼叫
			items = await itemApi.getAll(searchQuery, sortOrder);
		} catch (err: any) {
			error = err.message;
		}
	}

	function handleSearch() {
		clearTimeout(searchTimeout);
		searchTimeout = setTimeout(() => {
			loadItems();
		}, 500);
	}

	function startEdit(item: any) {
		editingId = Number(item.item_id);
		title = item.title;
		description = item.description || '';
		price = item.price;
		condition = item.condition;
		exchangeType = item.exchange_type;
		desiredItem = item.desired_item || '';
		window.scrollTo({ top: 0, behavior: 'smooth' });
	}

	function cancelEdit() {
		editingId = null;
		title = '';
		description = '';
		price = null;
		desiredItem = '';
		files = null;
		exchangeType = false;
	}

	async function handleDelete(id: any) {
		const numericId = Number(id);
		if (isNaN(numericId)) return alert('無效的商品 ID');

		if (!confirm('確定要刪除這件商品嗎？此動作無法復原。')) return;
		try {
			await itemApi.delete(numericId);
			alert('已成功刪除商品');
			await loadItems();
		} catch (err: any) {
			alert('刪除失敗：' + err.message);
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
		if (!exchangeType && price !== null && price > 1000000) {
			alert('價格不能超過 1,000,000');
			return;
		}

		uploadLoading = true;
		try {
			if (editingId) {
				const updateData = {
					title,
					description,
					price: exchangeType ? 0 : price || 0,
					condition,
					exchange_type: exchangeType,
					desired_item: exchangeType ? desiredItem : ''
				};
				await itemApi.update(editingId, updateData);
				alert('✅ 商品修改成功！');
			} else {
				const formData = new FormData();
				formData.append('title', title);
				formData.append('description', description);
				formData.append('condition', condition);
				formData.append('category', category.toString());
				formData.append('exchange_type', exchangeType.toString());
				formData.append('price', exchangeType ? '0' : price?.toString() || '0');
				if (exchangeType) formData.append('desired_item', desiredItem);
				if (files) {
					for (let i = 0; i < files.length; i++) {
						formData.append('images', files[i]);
					}
				}
				await itemApi.create(formData);
				alert('✨ 商品上架成功！');
			}
			cancelEdit();
			await loadItems();
		} catch (err: any) {
			alert('操作失敗：' + err.message);
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
	<div class="mx-auto mb-10 flex max-w-7xl items-center justify-between">
		<div>
			<h1 class="text-4xl font-black tracking-tight text-gray-900">二手交易市集</h1>
			<p class="mt-1 text-gray-500">找到你心儀的寶物，或是賦予舊愛新生命。</p>
		</div>
		<button
			on:click={logout}
			class="rounded-2xl border border-gray-200 bg-white px-6 py-2 font-bold text-gray-600 shadow-sm transition-all hover:border-red-100 hover:bg-red-50 hover:text-red-600"
		>
			登出系統
		</button>
	</div>

	<div class="mx-auto grid max-w-7xl grid-cols-1 gap-12 lg:grid-cols-12">
		<div class="lg:col-span-4">
			<div class="sticky top-12 rounded-[2rem] border border-gray-100 bg-white p-8 shadow-xl">
				<div class="mb-8 flex items-center">
					<div
						class="h-10 w-10 {editingId
							? 'bg-amber-500'
							: 'bg-blue-600'} mr-4 flex items-center justify-center rounded-xl text-white shadow-lg"
					>
						{#if editingId}
							<svg
								xmlns="http://www.w3.org/2000/svg"
								class="h-6 w-6"
								fill="none"
								viewBox="0 0 24 24"
								stroke="currentColor"
								><path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
								/></svg
							>
						{:else}
							<svg
								xmlns="http://www.w3.org/2000/svg"
								class="h-6 w-6"
								fill="none"
								viewBox="0 0 24 24"
								stroke="currentColor"
								><path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 4v16m8-8H4"
								/></svg
							>
						{/if}
					</div>
					<h2 class="text-2xl font-black text-gray-800">{editingId ? '編輯商品' : '我要上架'}</h2>
				</div>

				<div class="space-y-5">
					<div>
						<label for="title" class="mb-2 block text-sm font-bold text-gray-700">商品名稱</label>
						<input
							id="title"
							bind:value={title}
							placeholder="你想賣什麼？"
							class="w-full rounded-2xl border border-gray-200 bg-gray-50 p-4 outline-none focus:bg-white"
						/>
					</div>
					<div>
						<p class="mb-2 block text-sm font-bold text-gray-700">交易方式</p>
						<div class="flex space-x-4">
							<button
								type="button"
								class="flex-1 rounded-xl border-2 py-3 font-bold {exchangeType === false
									? 'border-blue-600 bg-blue-50 text-blue-700'
									: 'border-gray-200 text-gray-500'}"
								on:click={() => (exchangeType = false)}>💰 出售</button
							>
							<button
								type="button"
								class="flex-1 rounded-xl border-2 py-3 font-bold {exchangeType === true
									? 'border-purple-600 bg-purple-50 text-purple-700'
									: 'border-gray-200 text-gray-500'}"
								on:click={() => (exchangeType = true)}>🔄 交換</button
							>
						</div>
					</div>
					{#if !exchangeType}
						<div>
							<label for="price" class="mb-2 block text-sm font-bold text-gray-700"
								>售價 (NT$)</label
							>
							<input
								id="price"
								type="number"
								max="1000000"
								bind:value={price}
								class="w-full rounded-2xl border border-gray-200 bg-gray-50 p-4 font-bold text-blue-600 outline-none"
							/>
						</div>
					{:else}
						<div>
							<label for="desiredItem" class="mb-2 block text-sm font-bold text-gray-700"
								>想換什麼？</label
							>
							<input
								id="desiredItem"
								bind:value={desiredItem}
								class="w-full rounded-2xl border border-gray-200 bg-gray-50 p-4 outline-none"
							/>
						</div>
					{/if}
					<div>
						<label for="description" class="mb-2 block text-sm font-bold text-gray-700"
							>商品描述</label
						>
						<textarea
							id="description"
							bind:value={description}
							rows="4"
							class="w-full resize-none rounded-2xl border border-gray-200 bg-gray-50 p-4 outline-none"
						></textarea>
					</div>
					<div>
						<label for="condition-select" class="mb-2 block text-sm font-bold text-gray-700"
							>物品狀況</label
						>
						<select
							id="condition-select"
							bind:value={condition}
							class="w-full cursor-pointer rounded-2xl border border-gray-200 bg-gray-50 p-4 outline-none"
						>
							<option>全新</option><option>良好</option><option>普通</option><option>損壞</option>
						</select>
					</div>
					{#if !editingId}
						<div>
							<label for="product-images" class="mb-2 block text-sm font-bold text-gray-700"
								>商品照片</label
							>
							<div class="rounded-2xl border-2 border-dashed border-gray-200 p-6 text-center">
								<input
									id="product-images"
									type="file"
									multiple
									on:change={(e) => (files = e.currentTarget.files)}
									class="w-full cursor-pointer text-xs text-gray-500"
								/>
							</div>
						</div>
					{/if}
					<button
						on:click={handleCreate}
						disabled={uploadLoading}
						class="w-full {editingId
							? 'bg-amber-500'
							: 'bg-blue-600'} rounded-2xl py-5 text-lg font-black text-white shadow-lg disabled:bg-gray-300"
					>
						{uploadLoading ? '處理中...' : editingId ? '確認修改商品' : '確認發佈商品'}
					</button>
					{#if editingId}
						<button
							on:click={cancelEdit}
							class="w-full rounded-2xl bg-gray-100 py-3 font-bold text-gray-500 hover:bg-gray-200"
							>取消編輯</button
						>
					{/if}
				</div>
			</div>
		</div>

		<div class="lg:col-span-8">
			<div class="mb-8 flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
				<h2 class="flex items-center text-2xl font-black text-gray-800">
					<span class="mr-3 h-8 w-2 rounded-full bg-emerald-500"></span>熱門商品
				</h2>
				<div class="flex w-full max-w-md gap-2">
					<div class="relative flex-1">
						<input
							type="text"
							placeholder="搜尋..."
							bind:value={searchQuery}
							on:input={handleSearch}
							class="w-full rounded-xl border border-gray-200 bg-white py-2 pr-4 pl-10 text-sm outline-none focus:ring-2 focus:ring-blue-500"
						/>
					</div>
					<select
						bind:value={sortOrder}
						on:change={loadItems}
						class="rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm outline-none"
					>
						<option value="newest">最新上架</option><option value="price_asc">低到高</option><option
							value="price_desc">高到低</option
						>
					</select>
				</div>
			</div>
			{#if loading}
				<div class="flex flex-col items-center justify-center py-24">
					<div class="mb-4 h-12 w-12 animate-spin rounded-full border-b-2 border-blue-600"></div>
				</div>
			{:else}
				<div class="grid grid-cols-1 gap-8 md:grid-cols-2">
					{#each items as item}
						<div
							class="group flex flex-col overflow-hidden rounded-[2rem] border border-gray-100 bg-white shadow-sm hover:shadow-2xl"
						>
							<div class="relative h-56 overflow-hidden bg-gray-100">
								{#if item.images && item.images.length > 0}
									<img
										src={`${getFullImageUrl(item.images[0])}`}
										class="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
										alt={item.title}
									/>
								{/if}
							</div>
							<div class="flex-1 p-8">
								<h3 class="mb-3 text-2xl font-black text-gray-800">{item.title}</h3>
								<div class="mt-auto flex items-center justify-between border-t pt-6">
									<span class="text-3xl font-black text-emerald-600"
										>NT$ {item.price.toLocaleString()}</span
									>
									<div class="flex space-x-2">
										{#if item.owner_id === currentUserId}
											<button
												on:click={() => startEdit(item)}
												class="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50 text-amber-600 shadow-sm transition-all hover:bg-amber-500 hover:text-white"
												title="編輯商品"
												><svg
													xmlns="http://www.w3.org/2000/svg"
													class="h-5 w-5"
													fill="none"
													viewBox="0 0 24 24"
													stroke="currentColor"
													><path
														stroke-linecap="round"
														stroke-linejoin="round"
														stroke-width="2"
														d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
													/></svg
												></button
											>
											<button
												on:click={() => handleDelete(item.item_id)}
												class="flex h-10 w-10 items-center justify-center rounded-xl bg-red-50 text-red-600 shadow-sm transition-all hover:bg-red-500 hover:text-white"
												title="刪除商品"
												><svg
													xmlns="http://www.w3.org/2000/svg"
													class="h-5 w-5"
													fill="none"
													viewBox="0 0 24 24"
													stroke="currentColor"
													><path
														stroke-linecap="round"
														stroke-linejoin="round"
														stroke-width="2"
														d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
													/></svg
												></button
											>
										{/if}
										<button
											on:click={() => goto(`/items/${item.item_id}`)}
											class="flex h-10 w-10 items-center justify-center rounded-xl bg-gray-900 text-white shadow-sm transition-all hover:bg-blue-600"
											aria-label="View item details"
											><svg
												xmlns="http://www.w3.org/2000/svg"
												class="h-5 w-5"
												fill="none"
												viewBox="0 0 24 24"
												stroke="currentColor"
												><path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M14 5l7 7m0 0l-7 7m7-7H3"
												/></svg
											></button
										>
									</div>
								</div>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	</div>
</div>
