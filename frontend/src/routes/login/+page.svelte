<script lang="ts">
	import { authApi } from '$lib/api'; 
	import { goto } from '$app/navigation';

	let isLogin = true;
	let username = '';
	let password = '';
	let email = '';
	let address = '';
	let errorMessage = '';
	let loading = false;

	async function handleSubmit() {
		errorMessage = '';
		loading = true;

		// 準備資料
		const payload = isLogin 
			? { username, password } 
			: { username, email, password, address: address || "未提供", phones: [] };

		console.log("📝 頁面準備傳送的物件:", payload);

		try {
			if (isLogin) {
				const data = await authApi.login(payload);
				if (data && data.access_token) {
					localStorage.setItem('token', data.access_token);
					alert('登入成功！');
					goto('/items'); 
				}
			} else {
				await authApi.register(payload);
				alert('註冊成功！');
				isLogin = true;
			}
		} catch (err: any) {
			errorMessage = err.message;
		} finally {
			loading = false;
		}
	}
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-50 px-4">
	<div class="max-w-md w-full bg-white p-10 rounded-2xl shadow-xl border">
		<h2 class="text-3xl font-black text-center mb-8">{isLogin ? '歡迎回來' : '註冊帳號'}</h2>

		<form class="space-y-6" on:submit|preventDefault={handleSubmit}>
			<div class="space-y-4">
				<input bind:value={username} type="text" required class="block w-full px-4 py-3 border rounded-xl" placeholder="帳號">
				{#if !isLogin}
					<input bind:value={email} type="email" required class="block w-full px-4 py-3 border rounded-xl" placeholder="Email">
					<input bind:value={address} type="text" class="block w-full px-4 py-3 border rounded-xl" placeholder="地址">
				{/if}
				<input bind:value={password} type="password" required class="block w-full px-4 py-3 border rounded-xl" placeholder="密碼">
			</div>

			{#if errorMessage}
				<div class="p-3 text-sm text-red-600 bg-red-50 rounded-lg">⚠️ {errorMessage}</div>
			{/if}

			<button disabled={loading} type="submit" class="w-full py-4 bg-blue-600 text-white rounded-xl font-bold transition">
				{loading ? '請稍候...' : (isLogin ? '立即登入' : '完成註冊')}
			</button>
		</form>

		<button on:click={() => { isLogin = !isLogin; errorMessage = ''; }} class="w-full mt-4 text-center text-sm text-blue-600">
			{isLogin ? '切換註冊' : '切換登入'}
		</button>
	</div>
</div>