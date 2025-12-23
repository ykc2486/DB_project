<script lang="ts">
    import { onMount } from 'svelte';
    import { transactionApi } from '$lib/api';

    let transactions: any[] = [];
    let error = '';
    let loading = true;

    onMount(async () => {
        try {
            transactions = await transactionApi.getAll();
        } catch (e: any) {
            error = e.message;
        } finally {
            loading = false;
        }
    });

    async function updateStatus(id: number, status: string) {
        try {
            await transactionApi.updateStatus(id, status);
            transactions = await transactionApi.getAll(); // Refresh list
        } catch (e: any) {
            alert(e.message);
        }
    }
</script>

<div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">交易紀錄</h1>

    {#if loading}
        <p>載入中...</p>
    {:else if error}
        <p class="text-red-500">{error}</p>
    {:else if transactions.length === 0}
        <p>目前沒有交易紀錄。</p>
    {:else}
        <div class="grid gap-4">
            {#each transactions as t}
                <div class="border p-4 rounded shadow flex justify-between items-center">
                    <div>
                        <h2 class="text-xl font-semibold">{t.item?.title || '未知商品'}</h2>
                        <p class="text-gray-600">狀態: {t.status}</p>
                        <p class="text-sm text-gray-500">交易日期: {new Date(t.transaction_date).toLocaleDateString()}</p>
                        <p class="text-sm">買家 ID: {t.buyer_id} | 賣家 ID: {t.seller_id}</p>
                    </div>
                    <div class="flex gap-2">
                        {#if t.status === 'pending'}
                            <button 
                                class="bg-green-500 text-white px-3 py-1 rounded hover:bg-green-600"
                                on:click={() => updateStatus(t.transaction_id, 'completed')}
                            >
                                完成交易
                            </button>
                            <button 
                                class="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600"
                                on:click={() => updateStatus(t.transaction_id, 'cancelled')}
                            >
                                取消交易
                            </button>
                        {/if}
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</div>
