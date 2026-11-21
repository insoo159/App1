// 編譯時把網頁程式轉成舊版 Android WebView（Chrome 60 以上）也看得懂的寫法
const fs=require('fs'),es=require('esbuild');
let h=fs.readFileSync('www/index.html','utf8');
h=h.replace(/<script>([\s\S]*?)<\/script>/,(m,c)=>'<script>'+es.transformSync(c,{target:'chrome60'}).code.replace(/<\/script/gi,'<\\/script')+'</script>');
h=h.replace(/<style>([\s\S]*?)<\/style>/,(m,c)=>'<style>'+es.transformSync(c,{loader:'css',target:'chrome60'}).code+'</style>');
fs.writeFileSync('www/index.html',h);
console.log('compat done',h.length);
