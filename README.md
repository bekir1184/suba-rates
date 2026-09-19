# suba-rates

Suba'nın kur dosyası.

Uygulama farklı para birimlerindeki ödemeleri ana para biriminde toplarken
Avrupa Merkez Bankası'nın günlük referans kurlarını kullanıyor. Her telefonun
ücretsiz kur servisine ayrı ayrı gitmesi yerine kurlar burada günde birkaç kez
okunup tek bir dosya olarak yayımlanıyor: <https://rates.suba.info/rates.json>

- `scripts/build_rates.py` — kaynaktan okuyup `public/rates.json` üretir.
  Birincil kaynak frankfurter.dev, yedeği ECB'nin kendi XML dosyası.
- `.github/workflows/rates.yml` — altı saatte bir çalışır, değişiklik varsa
  işler ve GitHub Pages'e yayımlar.

Uygulamanın içinde bir de anlık görüntü var: ilk açılışta, çevrimdışıyken ve
bu dosyaya ulaşılamadığında o kullanılıyor. Kur bulunamayan bir para birimi
toplama hiç katılmaz; uydurulmuş bir rakam eksik rakamdan kötüdür.
