<script lang="ts">
    import { onMount } from 'svelte';
    import { messageApi } from '$lib/api';

    let conversations: any[] = [];
    let error = '';
    let loading = true;

    onMount(async () => {
        try {
            conversations = await messageApi.getConversations();
        } catch (e: any) {
            error = e.message;
        } finally {
            loading = false;
        }
    });
</script>

<div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">訊息中心</h1>

    {#if loading}
        <p>載入中...</p>
    {:else if error}
        <p class="text-red-500">{error}</p>
    {:else if conversations.length === 0}
        <p>目前沒有對話紀錄。</p>
    {:else}
        <div class="grid gap-4">
            {#each conversations as user}
                <a href="/messages/{user.user_id}" class="block border p-4 rounded shadow hover:bg-gray-50">
                    <h2 class="text-xl font-semibold">{user.username}</h2>
                    <p class="text-gray-600">{user.email}</p>
                </a>
            {/each}
        </div>
    {/if}
</div>
