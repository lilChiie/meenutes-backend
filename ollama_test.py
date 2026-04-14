import requests
import json

# teks yang mau diringkas
text = """
Yang 15 atau koneksi apapun itu nanti akan dicari tahu terus minta tolong itunya difasilitasi. Kalau ini nilai plusnya aja sih kalau bedanya. Tapi kalau memang terlalu berat ya nggak ada masalah. Yang jelas fungsi dasar yang saya inginkan ya cuma sebatas. Lebih bagus lagi karena kan memang setiap meeting harusnya punya record history seperti itu. Dan mungkin tingkatnya yang tingkatnya agak lumayan tinggi. Ya karena memang butuh integrasi sama ya sama ya dia itu. Masuk ke dalam sistemnya itu nanti sesuai dengan tabletnya. Jadi setiap meeting room nanti jadinya akan ada satu tablet yang memang fungsinya buat itu tadi. Bulanan ya sekarang ini kan dapet project. Nah nanti kalau sudah selesai nanti dari pengamatan atau yang lainnya akan memberi tugas yang lain lagi. Karena memang tugas kita di sini ya. Pada email tentang ini. Kontes ini tentang teknologi tentang negeri ini saya belum baca tapi jelas ini tentang. Dikonteskan jadi kita itu. Hal tentang sistem yang bisa dipakai di SI terus dia modelnya model robot itu roboh. Silahkan nanti kita akan bareng bareng diskusi tersubmit. Ini. Bisa jadi juga kita disuruh sampai ke Jepang sana. Tapi ya, tapi kita itu bersaing di sini disebutkan. Itu. Sama sama. Dari yang bisa yang ada otomatisasi yang kita otomatisasi belum ada berarti itu. Di software di tempat kita terus kita ajukan ajuin ke? Di sini dia itu kayak. Kontes kalau sampai nanti coba nanti kita akan cek yang mana diri kita yang bisa buat di software software kita. Kalau memang belum ada ya mungkin kita bisa menciptakan seperti. Kita yang harus ada implementasi segi sini supaya nanti dijual lagi sama mereka ini ujungnya seperti kayak gitu. Jadi software yang kita buat kita terus pakai di sini kita diajuin ke sana. Kalau memang mereka menang terus mereka ini dipakai sama mereka buat dijual balik lagi ke. Wah semuanya nanti kita coba masih Oktober sekarang September Oktober tentang lagi. Kemudian ini salah satunya. Sama di sini juga saya memastikan ke timur. Ini kita ada sby kompetition nanti ini. Ini nanti kita gunain buat tampil di ulang tahun sby yang jelasin di sini. Terus adik makan juga enggak makan diwajibkan mana? Mau punya kulit mo salah satu tuh enggak ada masalah.
"""

# prompt untuk ringkasan berpoin
prompt = f"""
Teks berikut mungkin berisi Bahasa Indonesia, Jepang, atau Inggris.

Tolong ringkas teks tersebut menjadi poin-poin pendek dalam Bahasa Indonesia.
Gunakan gaya bullet points (•) dan buat setiap poin maksimal satu kalimat.

Teks:
{text}
"""

# kirim request ke Ollama
response = requests.post("http://localhost:11434/api/generate", json={
    "model": "llama3",
    "prompt": prompt,
    "stream": False
})

# ambil hasil
data = response.json()
print("\n=== HASIL RINGKASAN DALAM POIN ===\n")
print(data["response"])
