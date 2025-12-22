<script lang="ts">
	import '../app.css';
</script>

<nav class="bg-gray-800 text-white p-4 shadow-lg">
	<div class="container mx-auto flex justify-between items-center">
		<a href="/" class="text-xl font-bold hover:text-blue-400">二手交易系統</a>
		<div class="space-x-6">
			<a href="/" class="hover:text-blue-400">首頁</a>
			<a href="/items" class="hover:text-blue-400">商品管理</a>
			<a href="/login" class="bg-blue-600 px-4 py-2 rounded hover:bg-blue-700 transition">登入 / 註冊</a>
		</div>
	</div>
</nav>

<main class="container mx-auto mt-8 p-4">
	<slot />
</main>