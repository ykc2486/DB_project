<script lang="ts">
	import { onMount } from 'svelte';
	import { itemApi } from '$lib/api';
	import { goto } from '$app/navigation';

	// 狀態變數
	let items: any[] = [];
	let loading = true;
	let error = '';

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
		await loadItems();
	});

	async function loadItems() {
		try {
			loading = true;
			error = '';
			// 呼叫 API 時傳入搜尋與排序條件，達成 Additional Feature 要求
			items = await itemApi.getAll(searchQuery, sortOrder);
		} catch (err: any) {
			error = err.message;
		} finally {
			loading = false;
		}
	}

	// 處理搜尋輸入 (Debounce 機制：使用者停止輸入 0.5 秒後才觸發，減少後端負擔)
	function handleSearch() {
		clearTimeout(searchTimeout);
		searchTimeout = setTimeout(() => {
			loadItems();
		}, 500);
	}

	// 進入編輯模式
	function startEdit(item: any) {
		editingId = item.item_id;
		title = item.title;
		description = item.description || '';
		price = item.price;
		condition = item.condition;
		exchangeType = item.exchange_type;
		desiredItem = item.desired_item || '';
		// 捲動到頂部表單位置
		window.scrollTo({ top: 0, behavior: 'smooth' });
	}

	// 取消編輯
	function cancelEdit() {
		editingId = null;
		title = '';
		description = '';
		price = null;
		desiredItem = '';
		files = null;
		exchangeType = false;
	}

	// 刪除功能
	async function handleDelete(id: number) {
		if (!confirm('確定要刪除這件商品嗎？此動作無法復原。')) return;
		try {
			await itemApi.delete(id);
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

		uploadLoading = true;

		try {
			if (editingId) {
				// Update 邏輯
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
				// 原有的 Create 邏輯
				const formData = new FormData();
				formData.append('title', title);
				formData.append('description', description);
				formData.append('condition', condition);
				formData.append('category', category.toString());
				formData.append('exchange_type', exchangeType.toString());

				if (exchangeType) {
					formData.append('desired_item', desiredItem);
					formData.append('price', '0');
				} else {
					formData.append('price', price?.toString() || '0');
				}

				if (files) {
					for (let i = 0; i < files.length; i++) {
						formData.append('images', files[i]);
					}
				}
				await itemApi.create(formData);
				alert('✨ 商品上架成功！');
			}

			cancelEdit(); // 重置表單與狀態
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
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
								/>
							</svg>
						{:else}
							<svg
								xmlns="http://www.w3.org/2000/svg"
								class="h-6 w-6"
								fill="none"
								viewBox="0 0 24 24"
								stroke="currentColor"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 4v16m8-8H4"
								/>
							</svg>
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
							class="w-full rounded-2xl border border-gray-200 bg-gray-50 p-4 transition-all outline-none focus:bg-white"
						/>
					</div>

					<div>
						<label for="transaction-type" class="mb-2 block text-sm font-bold text-gray-700"
							>交易方式</label
						>
						<div id="transaction-type" class="flex space-x-4">
							<button
								class="flex-1 rounded-xl border-2 py-3 font-bold transition-all {exchangeType ===
								false
									? 'border-blue-600 bg-blue-50 text-blue-700'
									: 'border-gray-200 text-gray-500'}"
								on:click={() => (exchangeType = false)}>💰 出售</button
							>
							<button
								class="flex-1 rounded-xl border-2 py-3 font-bold transition-all {exchangeType ===
								true
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
								bind:value={price}
								placeholder="0"
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
								placeholder="例如：PS5 遊戲片..."
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

					<div class="space-y-3 pt-2">
						<button
							on:click={handleCreate}
							disabled={uploadLoading}
							class="w-full {editingId
								? 'bg-amber-500 hover:bg-amber-600'
								: 'bg-blue-600 hover:bg-blue-700'} rounded-2xl py-5 text-lg font-black text-white shadow-lg transition-all disabled:bg-gray-300"
						>
							{uploadLoading ? '處理中...' : editingId ? '確認修改商品' : '確認發佈商品'}
						</button>

						{#if editingId}
							<button
								on:click={cancelEdit}
								class="w-full rounded-2xl bg-gray-100 py-3 font-bold text-gray-500 transition-all hover:bg-gray-200"
							>
								取消編輯
							</button>
						{/if}
					</div>
				</div>
			</div>
		</div>

		<div class="lg:col-span-8">
			<div class="mb-8 flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
				<h2 class="flex items-center text-2xl font-black text-gray-800">
					<span class="mr-3 h-8 w-2 rounded-full bg-emerald-500"></span>
					熱門商品
				</h2>

				<div class="flex w-full max-w-md gap-2">
					<div class="relative flex-1">
						<input
							type="text"
							placeholder="搜尋商品名稱或描述..."
							bind:value={searchQuery}
							on:input={handleSearch}
							class="w-full rounded-xl border border-gray-200 bg-white py-2 pl-10 pr-4 text-sm outline-none focus:ring-2 focus:ring-blue-500"
						/>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="absolute left-3 top-2.5 h-4 w-4 text-gray-400"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
							/>
						</svg>
					</div>

					<select
						bind:value={sortOrder}
						on:change={loadItems}
						class="cursor-pointer rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
					>
						<option value="newest">最新上架</option>
						<option value="price_asc">價格：低到高</option>
						<option value="price_desc">價格：高到低</option>
					</select>
				</div>
			</div>

			{#if loading}
				<div class="flex flex-col items-center justify-center py-24">
					<div class="mb-4 h-12 w-12 animate-spin rounded-full border-b-2 border-blue-600"></div>
					<p class="font-medium text-gray-400">正在為您搬運貨物...</p>
				</div>
			{:else if error}
				<div class="rounded-3xl border border-red-100 bg-red-50 p-6 font-bold text-red-600">
					⚠️ {error}
				</div>
			{:else if items.length === 0}
				<div class="rounded-[2rem] border-2 border-dashed border-gray-200 bg-white py-32 text-center">
					<p class="text-lg text-gray-400">找不到符合條件的商品。</p>
				</div>
			{:else}
				<div class="grid grid-cols-1 gap-8 md:grid-cols-2">
					{#each items as item}
						<div
							class="group flex flex-col overflow-hidden rounded-[2rem] border border-gray-100 bg-white shadow-sm transition-all duration-500 hover:shadow-2xl"
						>
							<div class="relative h-56 overflow-hidden bg-gray-100">
								{#if item.images && item.images.length > 0}
									<img
										src={`http://localhost:8000${item.images[0]}`}
										class="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
										alt={item.title}
									/>
								{:else}
									<div
										class="flex h-full w-full items-center justify-center bg-gray-50 text-gray-300 italic"
									>
										No Image
									</div>
								{/if}
								<div
									class="absolute top-4 right-4 rounded-full bg-white/90 px-3 py-1 text-[10px] font-black tracking-widest text-gray-500 uppercase backdrop-blur"
								>
									{item.condition}
								</div>
							</div>

							<div class="flex-1 p-8">
								<h3
									class="mb-3 text-2xl font-black text-gray-800 transition-colors group-hover:text-blue-600"
								>
									{item.title}
								</h3>
								<p class="mb-6 line-clamp-2 text-sm leading-relaxed text-gray-500">
									{item.description || '這件商品還沒有描述...'}
								</p>

								<div class="mt-auto flex items-center justify-between border-t border-gray-50 pt-6">
									<div class="flex flex-col">
										{#if !item.exchange_type}
											<span
												class="mb-1 text-[10px] font-black tracking-tighter text-gray-400 uppercase"
												>售價</span
											>
											<span class="text-3xl font-black tracking-tighter text-emerald-600">
												<span class="mr-0.5 text-sm font-bold">NT$</span
												>{item.price.toLocaleString()}
											</span>
										{:else}
											<span
												class="mb-1 text-[10px] font-black tracking-tighter text-purple-400 uppercase"
												>交換</span
											>
											<span
												class="max-w-[150px] truncate text-xl font-black tracking-tighter text-purple-600"
											>
												{item.desired_item || '任何物品'}
											</span>
										{/if}
									</div>

									<div class="flex space-x-2">
										<button
											on:click={() => startEdit(item)}
											class="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50 text-amber-600 shadow-sm transition-all hover:bg-amber-500 hover:text-white"
											title="編輯商品"
										>
											<svg
												xmlns="http://www.w3.org/2000/svg"
												class="h-5 w-5"
												fill="none"
												viewBox="0 0 24 24"
												stroke="currentColor"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
												/>
											</svg>
										</button>
										<button
											on:click={() => handleDelete(item.item_id)}
											class="flex h-10 w-10 items-center justify-center rounded-xl bg-red-50 text-red-600 shadow-sm transition-all hover:bg-red-500 hover:text-white"
											title="刪除商品"
										>
											<svg
												xmlns="http://www.w3.org/2000/svg"
												class="h-5 w-5"
												fill="none"
												viewBox="0 0 24 24"
												stroke="currentColor"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
												/>
											</svg>
										</button>
										<button
											on:click={() => goto(`/items/${item.item_id}`)}
											class="flex h-10 w-10 items-center justify-center rounded-xl bg-gray-900 text-white shadow-lg shadow-gray-200 transition-all hover:bg-blue-600"
										>
											<svg
												xmlns="http://www.w3.org/2000/svg"
												class="h-5 w-5"
												fill="none"
												viewBox="0 0 24 24"
												stroke="currentColor"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M14 5l7 7m0 0l-7 7m7-7H3"
												/>
											</svg>
										</button>
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