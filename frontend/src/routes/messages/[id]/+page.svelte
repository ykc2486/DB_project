<script lang="ts">
    import { onMount, afterUpdate } from 'svelte';
    import { page } from '$app/stores';
    import { messageApi, userApi } from '$lib/api';

    let messages: any[] = [];
    let currentUser: any = null;
    let newMessage = '';
    let error = '';
    let loading = true;
    let chatContainer: HTMLElement;

    const otherUserId = parseInt($page.params.id || '0');

    onMount(async () => {
        try {
            const [msgs, user] = await Promise.all([
                messageApi.getHistory(otherUserId),
                userApi.getProfile()
            ]);
            messages = msgs;
            currentUser = user;
        } catch (e: any) {
            error = e.message;
        } finally {
            loading = false;
        }
    });

    afterUpdate(() => {
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    });

    async function sendMessage() {
        if (!newMessage.trim()) return;
        try {
            const sentMsg = await messageApi.send(otherUserId, newMessage);
            messages = [...messages, sentMsg];
            newMessage = '';
        } catch (e: any) {
            alert(e.message);
        }
    }
</script>

<div class="container mx-auto p-4 h-[calc(100vh-4rem)] flex flex-col">
    <h1 class="text-2xl font-bold mb-4">聊天室</h1>

    {#if loading}
        <p>載入中...</p>
    {:else if error}
        <p class="text-red-500">{error}</p>
    {:else}
        <div class="flex-1 overflow-y-auto border rounded p-4 mb-4 bg-gray-50" bind:this={chatContainer}>
            {#if messages.length === 0}
                <p class="text-center text-gray-500">尚無訊息，開始聊天吧！</p>
            {:else}
                <div class="flex flex-col gap-2">
                    {#each messages as msg}
                        <div class={`p-2 rounded max-w-[70%] ${msg.sender_id === currentUser.user_id ? 'bg-blue-500 text-white self-end' : 'bg-white border self-start'}`}>
                            <p>{msg.content}</p>
                            <span class="text-xs opacity-75 block text-right mt-1">
                                {new Date(msg.sent_at).toLocaleTimeString()}
                            </span>
                        </div>
                    {/each}
                </div>
            {/if}
        </div>

        <div class="flex gap-2">
            <input 
                type="text" 
                class="flex-1 border p-2 rounded"
                placeholder="輸入訊息..."
                bind:value={newMessage}
                on:keydown={(e) => e.key === 'Enter' && sendMessage()}
            />
            <button 
                class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                on:click={sendMessage}
            >
                發送
            </button>
        </div>
    {/if}
</div>
