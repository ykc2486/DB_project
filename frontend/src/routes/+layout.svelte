<script lang="ts">
	import '../app.css';
</script>

<nav class="bg-gray-800 text-white p-4 shadow-lg">
	<div class="container mx-auto flex justify-between items-center">
		<a href="/" class="text-xl font-bold hover:text-blue-400">二手交易系統</a>
		<div class="space-x-6 flex items-center">
			<a href="/" class="hover:text-blue-400 transition-colors">首頁</a>
			<a href="/items" class="hover:text-blue-400 transition-colors">瀏覽市集</a>
			<a href="/transactions" class="hover:text-blue-400 transition-colors">交易紀錄</a>
			<a href="/messages" class="hover:text-blue-400 transition-colors">訊息</a>
			<a href="/wishlist" class="hover:text-pink-400 transition-colors flex items-center gap-1">
				<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
				</svg>
				收藏
			</a>
			<a href="/profile" class="hover:text-blue-400 transition-colors">個人檔案</a>
			<a href="/login" class="bg-blue-600 px-4 py-2 rounded-lg font-bold hover:bg-blue-700 transition-all shadow-lg shadow-blue-900/50">登入 / 註冊</a>
		</div>
	</div>
</nav>

<main class="container mx-auto mt-8 p-4">
	<slot />
</main>