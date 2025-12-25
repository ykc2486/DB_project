<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { transactionApi } from '$lib/api';

	let transactions: any[] = [];
	let error = '';
	let loading = true;
	let filterStatus = 'all'; // 篩選狀態

	onMount(() => {
		const token = localStorage.getItem('token');
		if (!token) {
			goto('/login');
			return;
		}
		fetchTransactions();
	});

	async function fetchTransactions() {
		try {
			loading = true;
			transactions = await transactionApi.getAll();
		} catch (e: any) {
			error = e.message;
		} finally {
			loading = false;
		}
	}

	async function updateStatus(id: number, status: string) {
		try {
			await transactionApi.updateStatus(id, status);
			await fetchTransactions();
		} catch (e: any) {
			alert(e.message);
		}
	}

	async function deleteTransaction(id: number) {
		if (!confirm('確定要從列表中移除此紀錄嗎？')) return;
		try {
			await transactionApi.delete(id);
			await fetchTransactions();
		} catch (e: any) {
			alert(e.message);
		}
	}

	// 篩選邏輯 (實作 Additional Feature: Filter)
	$: filteredTransactions =
		filterStatus === 'all' ? transactions : transactions.filter((t) => t.status === filterStatus);

	// 狀態標籤樣式
	const statusColors: any = {
		pending: 'bg-amber-100 text-amber-700',
		completed: 'bg-emerald-100 text-emerald-700',
		cancelled: 'bg-gray-100 text-gray-500'
	};
</script>

<div class="mx-auto max-w-5xl p-8">
	<div class="mb-10 flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-black text-gray-900">交易管理中心</h1>
			<p class="mt-1 text-gray-500">追蹤您的買賣進度與歷史紀錄。</p>
		</div>

		<div class="flex items-center space-x-2 rounded-xl bg-gray-100 p-1">
			{#each ['all', 'pending', 'completed', 'cancelled'] as status}
				<button
					on:click={() => (filterStatus = status)}
					class="rounded-lg px-4 py-2 text-sm font-bold transition-all {filterStatus === status
						? 'bg-white text-blue-600 shadow-sm'
						: 'text-gray-500 hover:text-gray-700'}"
				>
					{status === 'all'
						? '全部'
						: status === 'pending'
							? '進行中'
							: status === 'completed'
								? '已完成'
								: '已取消'}
				</button>
			{/each}
		</div>
	</div>

	{#if loading}
		<div class="py-20 text-center text-gray-400">正在讀取交易數據...</div>
	{:else if error}
		<div class="rounded-2xl border border-red-100 bg-red-50 p-6 font-bold text-red-600">
			⚠️ {error}
		</div>
	{:else if filteredTransactions.length === 0}
		<div class="rounded-[2rem] border-2 border-dashed border-gray-200 bg-gray-50 py-20 text-center">
			<p class="text-gray-400">找不到符合條件的交易紀錄。</p>
		</div>
	{:else}
		<div class="space-y-4">
			{#each filteredTransactions as t}
				<div
					class="flex flex-col items-start justify-between gap-6 rounded-[1.5rem] border border-gray-100 bg-white p-6 shadow-sm md:flex-row md:items-center"
				>
					<div class="flex-1">
						<div class="mb-2 flex items-center gap-3">
							<h2 class="text-xl font-black text-gray-800">{t.item?.title || '未知商品'}</h2>
							<span
								class="rounded-full px-3 py-1 text-xs font-bold tracking-wider uppercase {statusColors[
									t.status
								]}"
							>
								{t.status}
							</span>
						</div>
						<div class="grid grid-cols-2 gap-x-8 gap-y-1 text-sm text-gray-500">
							<p><span class="font-medium text-gray-400">交易編號:</span> #{t.transaction_id}</p>
							<p>
								<span class="font-medium text-gray-400">日期:</span>
								{new Date(t.transaction_date).toLocaleDateString()}
							</p>
							<p><span class="font-medium text-gray-400">買家 ID:</span> {t.buyer_id}</p>
							<p><span class="font-medium text-gray-400">賣家 ID:</span> {t.seller_id}</p>
						</div>
					</div>

					<div class="flex w-full gap-3 md:w-auto">
						{#if t.status === 'pending'}
							<button
								on:click={() => updateStatus(t.transaction_id, 'completed')}
								class="flex-1 rounded-xl bg-emerald-600 px-5 py-2 font-bold text-white shadow-lg shadow-emerald-100 transition hover:bg-emerald-700 md:flex-none"
							>
								完成交易
							</button>
							<button
								on:click={() => updateStatus(t.transaction_id, 'cancelled')}
								class="flex-1 rounded-xl border border-gray-200 bg-white px-5 py-2 font-bold text-gray-600 transition hover:bg-red-50 hover:text-red-600 md:flex-none"
							>
								取消
							</button>
						{:else}
							<button
								on:click={() => deleteTransaction(t.transaction_id)}
								class="flex-1 p-2 text-gray-400 transition hover:text-red-500 md:flex-none"
								title="刪除紀錄"
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
						{/if}
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
