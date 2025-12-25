<script lang="ts">
	import { onMount, afterUpdate } from 'svelte';
	import { page } from '$app/stores';
	import { messageApi, userApi, itemApi } from '$lib/api';
	import { goto } from '$app/navigation';

	let messages: any[] = [];
	let currentUser: any = null;
	let otherUser: any = null;
	let targetItem: any = null;
	let newMessage = '';
	let error = '';
	let loading = true;
	let chatContainer: HTMLElement;

	// 解析 ID: 預期格式為 "userId_itemId"
	const idParam = $page.params.id || '';
	const parts = idParam.split('_');
	const otherUserId = parseInt(parts[0]);
	const itemId = parts.length > 1 ? parseInt(parts[1]) : null;

	onMount(async () => {
		const token = localStorage.getItem('token');
		if (!token) {
			goto('/login');
			return;
		}

		// 核心檢查：如果沒有 itemId 或解析失敗，顯示錯誤
		if (!itemId || isNaN(itemId) || isNaN(otherUserId)) {
			error = '無效的商品對話連結，請從商品頁面重新點擊「聯絡賣家」。';
			loading = false;
			return;
		}

		try {
			const [msgs, me, other, item] = await Promise.all([
				messageApi.getHistory(otherUserId, itemId),
				userApi.getProfile(),
				userApi.read_user_by_id(otherUserId),
				itemApi.getOne(itemId.toString())
			]);
			messages = msgs;
			currentUser = me;
			otherUser = other;
			targetItem = item;
		} catch (e: any) {
			error = e.message;
		} finally {
			loading = false;
		}
	});

	afterUpdate(() => {
		if (chatContainer) chatContainer.scrollTop = chatContainer.scrollHeight;
	});

	async function sendMessage() {
		if (!newMessage.trim() || !itemId) return;
		try {
			const sentMsg = await messageApi.send(otherUserId, newMessage, itemId);
			messages = [...messages, sentMsg];
			newMessage = '';
		} catch (e: any) {
			alert(e.message);
		}
	}
</script>

<div class="container mx-auto flex h-[calc(100vh-8rem)] max-w-4xl flex-col p-4">
	{#if loading}
		<div class="flex flex-1 flex-col items-center justify-center">
			<div class="mb-4 h-12 w-12 animate-spin rounded-full border-b-2 border-blue-600"></div>
			<p class="text-gray-400">載入對話中...</p>
		</div>
	{:else if error}
		<div class="rounded-[2rem] border border-red-100 bg-red-50 p-10 text-center text-red-600">
			<h2 class="mb-4 text-2xl font-black">⚠️ 錯誤</h2>
			<p class="mb-6">{error}</p>
			<button
				on:click={() => goto('/messages')}
				class="rounded-2xl bg-red-600 px-8 py-3 font-bold text-white shadow-lg">回到訊息中心</button
			>
		</div>
	{:else}
		<div class="mb-4 flex items-center justify-between rounded-2xl border bg-white p-6 shadow-sm">
			<div>
				<button on:click={() => goto(`/users/${otherUserId}`)} class="group text-left">
					<h2 class="text-2xl font-black text-gray-800 transition-colors group-hover:text-blue-600">
						{otherUser?.username || '用戶'}
					</h2>
					<p class="text-xs font-bold tracking-widest text-gray-400 uppercase">查看個人檔案</p>
				</button>
			</div>

			{#if targetItem}
				<div
					class="flex items-center gap-4 rounded-2xl border border-blue-100 bg-blue-50 px-4 py-2"
				>
					<div class="text-right">
						<p class="text-xs font-bold text-blue-400 uppercase">詢問商品</p>
						<p class="font-black text-blue-700">{targetItem.title}</p>
					</div>
					<div class="h-8 w-[1px] bg-blue-200"></div>
					<p class="text-lg font-black text-blue-600">NT$ {targetItem.price}</p>
				</div>
			{/if}
		</div>

		<div
			class="mb-4 flex-1 overflow-y-auto rounded-[2rem] border bg-gray-50 p-6 shadow-inner"
			bind:this={chatContainer}
		>
			<div class="flex flex-col gap-4">
				{#each messages as msg}
					<div
						class="flex flex-col {msg.sender_id === currentUser.user_id
							? 'items-end'
							: 'items-start'}"
					>
						<div
							class={`max-w-[70%] rounded-2xl px-4 py-2 ${msg.sender_id === currentUser.user_id ? 'rounded-tr-none bg-blue-600 text-white' : 'rounded-tl-none border bg-white text-gray-800'}`}
						>
							<p>{msg.content}</p>
						</div>
						<span class="mt-1 px-1 text-[10px] text-gray-400">
							{new Date(msg.sent_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
						</span>
					</div>
				{/each}
			</div>
		</div>

		<div class="flex gap-2 rounded-2xl border bg-white p-2 shadow-lg">
			<input
				type="text"
				class="flex-1 rounded-xl p-4 outline-none"
				placeholder="輸入訊息..."
				bind:value={newMessage}
				on:keydown={(e) => e.key === 'Enter' && sendMessage()}
			/>
			<button
				on:click={sendMessage}
				class="rounded-xl bg-blue-600 px-10 font-black text-white shadow-lg transition-all hover:bg-blue-700"
				>發送</button
			>
		</div>
	{/if}
</div>
