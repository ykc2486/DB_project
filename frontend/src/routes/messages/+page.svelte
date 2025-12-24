<script lang="ts">
	import { onMount } from 'svelte';
	import { messageApi } from '$lib/api';
	import { PUBLIC_BACKEND_URL } from '$env/static/public';
	import {getFullImageUrl} from '$lib/api';

	let conversations: any[] = [];
	let error = '';
	let loading = true;

	onMount(async () => {
		try {
			loading = true;
			conversations = await messageApi.getConversations();
		} catch (e: any) {
			error = e.message;
		} finally {
			loading = false;
		}
	});
</script>

<div class="container mx-auto max-w-4xl p-8">
	<h1 class="mb-8 text-3xl font-black text-gray-900">訊息中心</h1>

	{#if loading}
		<div class="flex justify-center py-20">
			<div class="h-12 w-12 animate-spin rounded-full border-b-2 border-blue-600"></div>
		</div>
	{:else if error}
		<div class="rounded-2xl border border-red-100 bg-red-50 p-6 font-bold text-red-600">
			⚠️ {error}
		</div>
	{:else if conversations.length === 0}
		<div class="rounded-[2rem] border-2 border-dashed border-gray-200 bg-white py-32 text-center">
			<p class="text-gray-400">目前沒有對話紀錄。</p>
		</div>
	{:else}
		<div class="grid gap-4">
			{#each conversations as conv}
				<!-- 修改 href 邏輯，確保參數正確傳遞 -->
				<a
					href="/messages/{conv.user_id}?itemId={conv.item_id}"
					class="flex items-center rounded-2xl border border-gray-100 bg-white p-6 shadow-sm transition-all hover:bg-gray-50 hover:shadow-md"
				>
					<div
						class="mr-6 flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-100 text-xl font-black text-blue-600"
					>
						{conv.username.charAt(0).toUpperCase()}
					</div>
					<div class="flex-1">
						<h2 class="text-xl font-bold text-gray-800">{conv.username}</h2>
						<p class="mt-1 text-sm font-bold text-blue-500">
							關於：{conv.item_title}
						</p>
					</div>
					{#if conv.item_image}
						<img
							src={`${getFullImageUrl(conv.item_image)}`}
							class="h-16 w-16 rounded-xl border border-gray-100 object-cover"
							alt="item"
						/>
					{/if}
				</a>
			{/each}
		</div>
	{/if}
</div>
