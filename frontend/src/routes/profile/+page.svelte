<script lang="ts">
	import { onMount } from 'svelte';
	import { userApi } from '$lib/api';
	import { goto } from '$app/navigation';

	let user: any = null;
	let loading = true;
	let error = '';

	// --- 編輯狀態 ---
	let isEditing = false;
	let editData = { username: '', email: '', address: '', phones: [] as string[] };
	let newPhone = '';

	onMount(async () => {
		const token = localStorage.getItem('token');
		if (!token) {
			goto('/login');
			return;
		}
		await loadProfile();
	});

	async function loadProfile() {
		try {
			loading = true;
			user = await userApi.getProfile();
			// 初始化編輯資料
			editData = {
				username: user.username,
				email: user.email,
				address: user.address || '',
				phones: [...(user.phones || [])]
			};
		} catch (err: any) {
			error = err.message;
		} finally {
			loading = false;
		}
	}

	async function handleUpdate() {
		try {
			await userApi.updateProfile(editData);
			alert('個人檔案已更新！');
			isEditing = false;
			await loadProfile();
		} catch (err: any) {
			alert(err.message);
		}
	}

	function addPhone() {
		if (newPhone && !editData.phones.includes(newPhone)) {
			editData.phones = [...editData.phones, newPhone];
			newPhone = '';
		}
	}

	function removePhone(p: string) {
		editData.phones = editData.phones.filter((phone) => phone !== p);
	}

	function logout() {
		localStorage.removeItem('token');
		goto('/login');
	}
</script>

<div class="min-h-screen bg-gray-50 p-4 md:p-12">
	<div class="mx-auto max-w-3xl">
		<div class="mb-10 flex items-center justify-between">
			<div class="flex items-center">
				<button
					on:click={() => goto('/items')}
					class="mr-6 rounded-full p-2 transition-colors hover:bg-gray-200"
					aria-label="Go to items"
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="h-6 w-6 text-gray-600"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M10 19l-7-7m0 0l7-7m-7 7h18"
						/>
					</svg>
				</button>
				<h1 class="text-4xl font-black tracking-tight text-gray-900">個人檔案</h1>
			</div>
			<div class="flex space-x-2">
				<button
					on:click={() => (isEditing = !isEditing)}
					class="rounded-2xl border border-gray-200 bg-white px-6 py-2 font-bold text-blue-600 shadow-sm transition-all hover:bg-blue-50"
				>
					{isEditing ? '取消編輯' : '編輯資料'}
				</button>
				<button
					on:click={logout}
					class="rounded-2xl border border-gray-200 bg-white px-6 py-2 font-bold text-red-600 shadow-sm transition-all hover:border-red-100 hover:bg-red-50"
				>
					登出
				</button>
			</div>
		</div>

		{#if loading}
			<div class="flex h-64 items-center justify-center">
				<div class="h-12 w-12 animate-spin rounded-full border-b-2 border-blue-600"></div>
			</div>
		{:else if error}
			<div
				class="rounded-2xl border border-red-100 bg-red-50 p-6 text-center font-medium text-red-600"
			>
				{error}
			</div>
		{:else if user}
			<div class="overflow-hidden rounded-[2.5rem] border border-gray-100 bg-white p-10 shadow-xl">
				{#if !isEditing}
					<div class="mb-10 flex items-center">
						<div
							class="mr-8 flex h-24 w-24 items-center justify-center rounded-full bg-blue-100 text-3xl font-black text-blue-600"
						>
							{user.username.charAt(0).toUpperCase()}
						</div>
						<div>
							<h2 class="text-3xl font-black text-gray-900">{user.username}</h2>
							<p class="font-medium text-gray-500">
								加入時間：{new Date(user.join_date).toLocaleDateString()}
							</p>
						</div>
					</div>
					<div class="grid grid-cols-1 gap-8 md:grid-cols-2">
						<div class="rounded-3xl bg-gray-50 p-6">
							<h3 class="mb-2 text-sm font-bold tracking-wider text-gray-400 uppercase">Email</h3>
							<p class="text-lg font-bold text-gray-800">{user.email}</p>
						</div>
						<div class="rounded-3xl bg-gray-50 p-6">
							<h3 class="mb-2 text-sm font-bold tracking-wider text-gray-400 uppercase">地址</h3>
							<p class="text-lg font-bold text-gray-800">{user.address || '未設定'}</p>
						</div>
						<div class="rounded-3xl bg-gray-50 p-6 md:col-span-2">
							<h3 class="mb-2 text-sm font-bold tracking-wider text-gray-400 uppercase">
								聯絡電話
							</h3>
							<div class="flex flex-wrap gap-3">
								{#each user.phones || [] as phone}
									<span
										class="rounded-xl border border-gray-100 bg-white px-4 py-2 font-bold text-gray-700 shadow-sm"
										>{phone}</span
									>
								{:else}
									<p class="text-gray-400 italic">未設定電話</p>
								{/each}
							</div>
						</div>
					</div>
				{:else}
					<div class="space-y-6">
						<h2 class="mb-6 text-2xl font-black">修改個人資料</h2>
						<div>
							<label for="edit-username" class="mb-2 block text-sm font-bold text-gray-400"
								>使用者名稱</label
							>
							<input
								id="edit-username"
								bind:value={editData.username}
								class="w-full rounded-2xl border bg-gray-50 p-4 outline-none focus:bg-white"
							/>
						</div>
						<div>
							<label for="edit-email" class="mb-2 block text-sm font-bold text-gray-400"
								>Email</label
							>
							<input
								id="edit-email"
								bind:value={editData.email}
								type="email"
								class="w-full rounded-2xl border bg-gray-50 p-4 outline-none focus:bg-white"
							/>
						</div>
						<div>
							<label for="edit-address" class="mb-2 block text-sm font-bold text-gray-400"
								>地址</label
							>
							<input
								id="edit-address"
								bind:value={editData.address}
								class="w-full rounded-2xl border bg-gray-50 p-4 outline-none focus:bg-white"
							/>
						</div>
						<div>
							<label for="edit-phone-input" class="mb-2 block text-sm font-bold text-gray-400"
								>聯絡電話</label
							>
							<div class="mb-3 flex gap-2">
								<input
									id="edit-phone-input"
									bind:value={newPhone}
									placeholder="新增電話..."
									class="flex-1 rounded-xl border bg-gray-50 p-3"
								/>
								<button
									type="button"
									on:click={addPhone}
									class="rounded-xl bg-blue-600 px-4 font-bold text-white">新增</button
								>
							</div>
							<div class="flex flex-wrap gap-2">
								{#each editData.phones as p}
									<span
										class="flex items-center rounded-lg bg-blue-50 px-3 py-1 font-bold text-blue-600"
									>
										{p}
										<button type="button" on:click={() => removePhone(p)} class="ml-2 text-red-400"
											>×</button
										>
									</span>
								{/each}
							</div>
						</div>
						<button
							on:click={handleUpdate}
							class="w-full rounded-2xl bg-blue-600 py-4 text-xl font-black text-white shadow-lg shadow-blue-100"
						>
							確認更新
						</button>
					</div>
				{/if}
			</div>
		{/if}
	</div>
</div>
