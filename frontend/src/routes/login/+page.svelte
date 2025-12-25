<script lang="ts">
	import { authApi } from '$lib/api';
	import { goto } from '$app/navigation';

	let isLogin = true; // 切換登入或註冊
	let username = '';
	let password = '';
	let email = '';
	let fullName = '';
	let errorMessage = '';
	let loading = false;

	async function handleSubmit() {
		errorMessage = '';
		loading = true;

		try {
			if (isLogin) {
				// 執行登入 (使用 FormData 格式)
				const formData = new FormData();
				formData.append('username', username);
				formData.append('password', password);

				const data = await authApi.login(formData);
				localStorage.setItem('token', data.access_token);
				alert('登入成功！');
				goto('/items'); // 登入後跳轉到商品頁
			} else {
				// 執行註冊
				await authApi.register({
					username,
					email,
					password,
					full_name: fullName
				});
				alert('註冊成功，請登入！');
				isLogin = true; // 註冊完自動切換到登入畫面
			}
		} catch (err: any) {
			errorMessage = err.message || '操作失敗，請檢查帳號密碼';
		} finally {
			loading = false;
		}
	}
</script>

<div class="min-h-[80-vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
	<div class="max-w-md w-full space-y-8 bg-white p-10 rounded-2xl shadow-xl border border-gray-100">
		<div>
			<h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
				{isLogin ? '歡迎回來' : '建立新帳號'}
			</h2>
			<p class="mt-2 text-center text-sm text-gray-600">
				{isLogin ? '請登入以管理您的商品' : '加入我們，開始進行二手交易'}
			</p>
		</div>

		<form class="mt-8 space-y-6" on:submit|preventDefault={handleSubmit}>
			<div class="rounded-md shadow-sm space-y-4">
				<div>
					<label for="username" class="sr-only">帳號</label>
					<input bind:value={username} id="username" type="text" required minlength="3" maxlength="24" class="appearance-none rounded-lg relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm" placeholder="帳號 (Username)">
				</div>

				{#if !isLogin}
					<div>
						<input bind:value={fullName} type="text" required class="appearance-none rounded-lg relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm" placeholder="全名 (Full Name)">
					</div>
					<div>
						<input bind:value={email} type="email" required class="appearance-none rounded-lg relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm" placeholder="電子郵件 (Email)">
					</div>
				{/if}

				<div>
					<label for="password" class="sr-only">密碼</label>
					<input bind:value={password} id="password" type="password" required minlength="8" class="appearance-none rounded-lg relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm" placeholder="密碼 (Password)">
				</div>
			</div>

			{#if errorMessage}
				<div class="text-red-500 text-sm text-center bg-red-50 py-2 rounded">
					{errorMessage}
				</div>
			{/if}

			<div>
				<button disabled={loading} type="submit" class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition">
					{loading ? '處理中...' : (isLogin ? '登入' : '註冊')}
				</button>
			</div>
		</form>

		<div class="text-center">
			<button on:click={() => isLogin = !isLogin} class="text-sm text-blue-600 hover:text-blue-500 font-medium">
				{isLogin ? '還沒有帳號？立即註冊' : '已經有帳號了？點此登入'}
			</button>
		</div>
	</div>
</div>