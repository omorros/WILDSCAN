-- Migration 003: Seed data for code_word_lexicon
-- ~100 entries covering Thai (th), Vietnamese (vi), English (en), Chinese (zh), Indonesian (id)
-- species_id references insertion order from 002_species.sql:
--   1=Loxodonta africana, 2=Elephas maximus, 3=Manis javanica, 4=Manis pentadactyla,
--   7=Ceratotherium simum, 8=Diceros bicornis, 9=Panthera tigris,
--   10=Eretmochelys imbricata, 14=Rhinoplax vigil, 15=Cacatua sulphurea,
--   17=Python reticulatus, 21=Ursus thibetanus, 22=Helarctos malayanus,
--   23=Sphyrna lewini, 26=Dalbergia cochinchinensis, 27=Dalbergia oliveri,
--   28=Hippocampus kuda, 32=Gekko gecko, 35=Scleropages formosus,
--   42=Moschus moschiferus

INSERT INTO code_word_lexicon
    (code_word, language, species_id, product_type, confidence,
     context_required, false_positive_contexts, obfuscation_variants,
     source, status)
VALUES

-- ============================================================
-- THAI (th) — ~20 entries
-- ============================================================

-- Ivory / Elephant
('งาช้าง', 'th', 1, 'ivory_raw', 0.95,
 '{}',
 ARRAY['พิพิธภัณฑ์','นิทรรศการ'],
 ARRAY['งา.ช้าง','งา ช้าง','ง4ช้4ง'],
 'TRAFFIC Thailand 2019', 'verified'),

('งาแกะสลัก', 'th', 1, 'ivory_worked', 0.88,
 ARRAY['ช้าง','ของเก่า'],
 ARRAY['พลาสติก','เรซิน'],
 ARRAY['งาแกะ.สลัก','งา_แกะสลัก'],
 'TRAFFIC Thailand 2019', 'verified'),

('ผงงา', 'th', 1, 'ivory_powder', 0.82,
 ARRAY['ช้าง','ยาแผนโบราณ'],
 ARRAY['ฟัน','ทันตแพทย์'],
 ARRAY['ผง.งา','p0ngnga'],
 'WWF-Thailand 2021', 'verified'),

-- Pangolin
('เกล็ดนิ่ม', 'th', 3, 'pangolin_scales', 0.91,
 '{}',
 ARRAY['ปลา','แมลง'],
 ARRAY['เกล็ด.นิ่ม','เกล็ดน.ิ่ม'],
 'TRAFFIC Thailand 2019', 'verified'),

('ลูกนิ่ม', 'th', 3, 'pangolin_live', 0.78,
 ARRAY['ขาย','ส่ง'],
 ARRAY['ตุ๊กตา','ของเล่น'],
 ARRAY['ลูก.นิ่ม','l00knim'],
 'Challender et al. 2019', 'verified'),

-- Tiger
('กระดูกเสือ', 'th', 9, 'tiger_bone', 0.93,
 '{}',
 ARRAY['สัตว์เลี้ยง','สวนสัตว์'],
 ARRAY['กระดูก.เสือ','กระด0กเสือ'],
 'EIA Thailand 2020', 'verified'),

('หนังเสือ', 'th', 9, 'tiger_skin', 0.90,
 '{}',
 ARRAY['สังเคราะห์','ผ้า'],
 ARRAY['หนัง.เสือ','หน4งเสือ'],
 'EIA Thailand 2020', 'verified'),

('เล็บเสือ', 'th', 9, 'tiger_claw', 0.85,
 ARRAY['ของเก่า','เครื่องราง'],
 ARRAY['ปลอม','พลาสติก'],
 ARRAY['เล็บ.เสือ','เล็บเส่ือ'],
 'TRAFFIC Thailand 2019', 'verified'),

-- Rhino
('นอแรด', 'th', 7, 'rhino_horn', 0.97,
 '{}',
 ARRAY['พิพิธภัณฑ์','ศิลปะ'],
 ARRAY['น0แรด','นอ.แรด','น0.แรด'],
 'TRAFFIC Thailand 2019', 'verified'),

('ผงนอแรด', 'th', 7, 'rhino_horn_powder', 0.94,
 ARRAY['ยา','สุขภาพ'],
 ARRAY['ยาแผนปัจจุบัน'],
 ARRAY['ผงน0แรด','ผง_นอแรด'],
 'UNODC 2020', 'verified'),

-- Bear
('น้ำดีหมี', 'th', 21, 'bear_bile', 0.89,
 ARRAY['ยา','สมุนไพร'],
 ARRAY['สังเคราะห์','วิตามิน'],
 ARRAY['น้ำดี.หมี','น้ำดีหม.ี'],
 'Animals Asia 2018', 'verified'),

('ดีหมี', 'th', 22, 'bear_bile', 0.87,
 ARRAY['ยา','แผนโบราณ'],
 ARRAY['สังเคราะห์'],
 ARRAY['ดี.หมี','ด1หมี'],
 'Animals Asia 2018', 'verified'),

-- Hornbill
('งาเหลือง', 'th', 14, 'hornbill_casque', 0.86,
 ARRAY['นก','หัว'],
 ARRAY['เทียม','พลาสติก'],
 ARRAY['งา.เหลือง','ง4เหลือง'],
 'EIA 2015', 'verified'),

('หัวนกชนหิน', 'th', 14, 'hornbill_casque', 0.92,
 '{}',
 ARRAY['สวนสัตว์'],
 ARRAY['หัวนก.ชนหิน','h4dnokchnhin'],
 'TRAFFIC Southeast Asia 2016', 'verified'),

-- Rosewood
('พะยูง', 'th', 26, 'rosewood_log', 0.88,
 ARRAY['ไม้','ท่อน'],
 ARRAY['เฟอร์นิเจอร์ถูกกฎหมาย','ใบอนุญาต'],
 ARRAY['พะ.ยูง','ph4yung'],
 'Forest Trends 2019', 'verified'),

('ไม้พะยูงแห้ง', 'th', 26, 'rosewood_processed', 0.83,
 ARRAY['ขาย','ราคา'],
 ARRAY['ใบอนุญาต','มีเอกสาร'],
 ARRAY['ไม้พะ.ยูง'],
 'Forest Trends 2019', 'verified'),

-- Turtle / Tortoiseshell
('กระ', 'th', 10, 'tortoiseshell', 0.72,
 ARRAY['กระดอง','เต่า','กำไล'],
 ARRAY['ปลากระ','กระโถน','กระดาน'],
 ARRAY['ก.ระ','kr4'],
 'TRAFFIC Thailand 2019', 'verified'),

('กระดองเต่า', 'th', 10, 'turtle_shell', 0.90,
 '{}',
 ARRAY['ของปลอม','เรซิน'],
 ARRAY['กระดอง.เต่า','krd0ngto'],
 'TRAFFIC Thailand 2019', 'verified'),

-- Cockatoo
('นกแก้วขาว', 'th', 15, 'live_bird', 0.80,
 ARRAY['ขาย','ลูก','ราคา'],
 ARRAY['สวนนก','อนุรักษ์'],
 ARRAY['นกแก้ว.ขาว'],
 'TRAFFIC Southeast Asia 2021', 'verified'),

-- Seahorse
('ม้าน้ำแห้ง', 'th', 28, 'seahorse_dried', 0.88,
 ARRAY['ยา','บำรุง'],
 ARRAY['ของเล่น','ตกแต่ง'],
 ARRAY['ม้าน้ำ.แห้ง','m4n4mheng'],
 'Project Seahorse 2018', 'verified'),

-- ============================================================
-- VIETNAMESE (vi) — ~25 entries
-- ============================================================

-- Ivory
('ngà voi', 'vi', 1, 'ivory_raw', 0.95,
 '{}',
 ARRAY['bảo tàng','triển lãm'],
 ARRAY['ng4 voi','ngà.voi','ng@voi'],
 'TRAFFIC Vietnam 2018', 'verified'),

('ngà voi thật', 'vi', 1, 'ivory_raw', 0.97,
 '{}',
 ARRAY['nhựa giả'],
 ARRAY['ngà voi th4t','ng@voi_th@t'],
 'ENV Vietnam 2020', 'verified'),

('tác phẩm ngà', 'vi', 1, 'ivory_worked', 0.85,
 ARRAY['điêu khắc','cổ vật'],
 ARRAY['nhựa','composite'],
 ARRAY['tac pham nga','t4c ph4m ng4'],
 'TRAFFIC Vietnam 2018', 'verified'),

-- Rhino horn
('sừng tê giác', 'vi', 7, 'rhino_horn', 0.98,
 '{}',
 ARRAY['bảo tàng','nghệ thuật'],
 ARRAY['sung te gi4c','s4ng_t3_gi4c','s.u.n.g t.e g.i.a.c'],
 'TRAFFIC Vietnam 2018', 'verified'),

('bột sừng tê', 'vi', 7, 'rhino_horn_powder', 0.95,
 ARRAY['thuốc','chữa bệnh'],
 ARRAY['dược phẩm hợp pháp'],
 ARRAY['bot sung te','b0t s4ng te'],
 'UNODC 2020', 'verified'),

('tê giác trắng', 'vi', 7, 'rhino_horn', 0.90,
 ARRAY['sừng','mua','bán'],
 ARRAY['vườn thú','bảo tồn'],
 ARRAY['te gi4c tr4ng'],
 'ENV Vietnam 2020', 'verified'),

-- Pangolin
('vảy tê tê', 'vi', 3, 'pangolin_scales', 0.93,
 '{}',
 ARRAY['mẫu vật','nghiên cứu'],
 ARRAY['v4y te te','v@y tê tê','vay.te.te'],
 'TRAFFIC Vietnam 2018', 'verified'),

('tê tê sống', 'vi', 3, 'pangolin_live', 0.91,
 ARRAY['bán','giá'],
 ARRAY['vườn thú'],
 ARRAY['te te s0ng','t3_t3_s0ng'],
 'Challender et al. 2019', 'verified'),

('cao tê tê', 'vi', 3, 'pangolin_medicine', 0.86,
 ARRAY['thuốc','bổ'],
 ARRAY['dược phẩm hợp pháp'],
 ARRAY['cao te te','c4o_te_te'],
 'Challender et al. 2019', 'verified'),

-- Tiger
('xương hổ', 'vi', 9, 'tiger_bone', 0.94,
 '{}',
 ARRAY['gấu','bò'],
 ARRAY['xuong h0','x4ong_h0','x.u.o.n.g h.o'],
 'EIA Vietnam 2021', 'verified'),

('cao hổ cốt', 'vi', 9, 'tiger_bone_glue', 0.97,
 '{}',
 ARRAY['cao bò','cao trâu'],
 ARRAY['cao ho cot','c4o h0 c0t','c.a.o h.o c.o.t'],
 'ENV Vietnam 2020', 'verified'),

('da hổ', 'vi', 9, 'tiger_skin', 0.92,
 '{}',
 ARRAY['vải','tổng hợp'],
 ARRAY['d4 h0','da.ho'],
 'EIA Vietnam 2021', 'verified'),

-- Tortoiseshell
('đồi mồi', 'vi', 10, 'tortoiseshell', 0.89,
 ARRAY['lược','vòng','hộp'],
 ARRAY['nhựa','imitation'],
 ARRAY['doi moi','đ0i m0i','d.o.i m.o.i'],
 'TRAFFIC Vietnam 2018', 'verified'),

('mai rùa biển', 'vi', 10, 'turtle_shell', 0.87,
 ARRAY['bán','thủ công'],
 ARRAY['nhựa giả','composite'],
 ARRAY['mai rua bien','m4i r4a bi4n'],
 'TRAFFIC Vietnam 2018', 'verified'),

-- Bear bile
('mật gấu', 'vi', 21, 'bear_bile', 0.93,
 ARRAY['thuốc','chữa'],
 ARRAY['dược phẩm hợp pháp','bò','lợn'],
 ARRAY['mat gau','m4t g4u','m.a.t g.a.u'],
 'Animals Asia 2018', 'verified'),

('cao gấu', 'vi', 21, 'bear_bile_paste', 0.88,
 ARRAY['thuốc','bổ'],
 ARRAY['cao bổ khác'],
 ARRAY['cao gau','c4o_g4u'],
 'Animals Asia 2018', 'verified'),

-- Rosewood
('gỗ trắc', 'vi', 27, 'rosewood_log', 0.87,
 ARRAY['gỗ','bán','tấm'],
 ARRAY['giấy phép','hợp pháp'],
 ARRAY['go trac','g0_tr4c'],
 'Forest Trends 2019', 'verified'),

('gỗ hương', 'vi', 26, 'rosewood_log', 0.84,
 ARRAY['gỗ','bán'],
 ARRAY['giấy phép','hợp pháp'],
 ARRAY['go huong','g0_hu0ng'],
 'ENV Vietnam 2020', 'verified'),

-- Seahorse
('hải mã khô', 'vi', 28, 'seahorse_dried', 0.90,
 ARRAY['thuốc','bổ thận'],
 ARRAY['đồ chơi','trang trí'],
 ARRAY['hai ma kho','h4i m4 kh0'],
 'Project Seahorse 2018', 'verified'),

('cá ngựa biển', 'vi', 28, 'seahorse_live', 0.82,
 ARRAY['bán','giá'],
 ARRAY['thủy cung','nuôi cảnh'],
 ARRAY['ca ngua bien','c4 ng4a bi4n'],
 'Project Seahorse 2018', 'verified'),

-- Shark fin
('vi cá mập', 'vi', 23, 'shark_fin', 0.88,
 ARRAY['bán','hàng'],
 ARRAY['nhà hàng hợp pháp','nhập khẩu có phép'],
 ARRAY['vi ca map','vi_c4_m4p'],
 'TRAFFIC SEAP 2020', 'verified'),

-- Tokay gecko
('tắc kè khô', 'vi', 32, 'gecko_dried', 0.86,
 ARRAY['thuốc','bán'],
 ARRAY['đồ chơi'],
 ARRAY['tac ke kho','t4c k4 kh0'],
 'Nijman et al. 2021', 'verified'),

('tắc kè sống', 'vi', 32, 'gecko_live', 0.83,
 ARRAY['bán','nuôi'],
 ARRAY['vườn thú'],
 ARRAY['tac ke song','t4c k4 s0ng'],
 'Nijman et al. 2021', 'verified'),

-- Arowana
('cá rồng', 'vi', 35, 'live_fish', 0.75,
 ARRAY['bán','giá','triệu'],
 ARRAY['trang trí','hợp pháp','có giấy phép'],
 ARRAY['ca rong','c4_r0ng'],
 'CITES Trade Database 2020', 'verified'),

-- Musk deer
('xạ hương', 'vi', 42, 'musk_pod', 0.83,
 ARRAY['thuốc','hương liệu'],
 ARRAY['tổng hợp','nước hoa thường'],
 ARRAY['xa huong','x4_hu0ng'],
 'TRAFFIC Vietnam 2018', 'verified'),

-- ============================================================
-- ENGLISH (en) — ~15 entries
-- ============================================================

('white gold', 'en', 1, 'ivory_raw', 0.65,
 ARRAY['tusk','carving','elephant','bone'],
 ARRAY['metal','jewelry','currency','investment'],
 ARRAY['wh1te gold','white g0ld','wh!te_gold'],
 'Harrison et al. 2016', 'verified'),

('bone carving', 'en', 1, 'ivory_worked', 0.60,
 ARRAY['elephant','mammoth','antique','tusk'],
 ARRAY['wood','stone','synthetic'],
 ARRAY['b0ne carving','bone_c4rving'],
 'Harrison et al. 2016', 'verified'),

('traditional medicine ingredients', 'en', 9, 'tiger_bone', 0.55,
 ARRAY['tiger','bear','rhino','rare'],
 ARRAY['herbal','plant-based','certified'],
 ARRAY['tradit10nal medicine','trad_med_ingredients'],
 'Xu et al. 2020', 'verified'),

('shahtoosh', 'en', NULL, 'shahtoosh_shawl', 0.97,
 '{}',
 ARRAY['pashmina','synthetic','wool'],
 ARRAY['sh4ht00sh','shahto0sh','s.h.a.h.t.o.o.s.h'],
 'TRAFFIC 2015', 'verified'),

('shark fin soup', 'en', 23, 'shark_fin', 0.82,
 ARRAY['sell','supply','wholesale','dried'],
 ARRAY['restaurant menu','legal import'],
 ARRAY['sh4rk fin','shark f!n s0up'],
 'Dent & Clarke 2015', 'verified'),

('rhino horn powder', 'en', 7, 'rhino_horn_powder', 0.96,
 '{}',
 ARRAY['synthetic','replica','antique'],
 ARRAY['rhin0 horn','rh!no h0rn p0wder'],
 'Milliken & Shaw 2012', 'verified'),

('tiger bone wine', 'en', 9, 'tiger_bone_wine', 0.93,
 '{}',
 ARRAY['synthetic','tiger-themed wine'],
 ARRAY['tiger b0ne','t!ger bone wine'],
 'EIA 2019', 'verified'),

('bear bile capsules', 'en', 21, 'bear_bile', 0.90,
 '{}',
 ARRAY['synthetic UDCA','plant-based'],
 ARRAY['bear b!le','b34r bile caps'],
 'Animals Asia 2018', 'verified'),

('pangolin scales', 'en', 3, 'pangolin_scales', 0.92,
 '{}',
 ARRAY['model','replica','keratinase'],
 ARRAY['p4ngolin sc4les','pangol1n scales'],
 'Challender et al. 2019', 'verified'),

('musk pod', 'en', 42, 'musk_pod', 0.85,
 ARRAY['deer','natural','medicine'],
 ARRAY['synthetic musk','fragrance compound'],
 ARRAY['musk p0d','m4sk pod'],
 'TRAFFIC 2015', 'verified'),

('tortoiseshell', 'en', 10, 'tortoiseshell', 0.88,
 ARRAY['genuine','real','antique','comb','bangle'],
 ARRAY['acrylic','plastic','imitation','faux'],
 ARRAY['tort0iseshell','torto!seshell','t0rtoiseshell'],
 'Lyons et al. 2017', 'verified'),

('hornbill casque', 'en', 14, 'hornbill_casque', 0.94,
 '{}',
 ARRAY['replica','resin','synthetic'],
 ARRAY['h0rnbill casque','hornb!ll c@sque'],
 'EIA 2015', 'verified'),

('ivory bangle', 'en', 1, 'ivory_worked', 0.87,
 ARRAY['genuine','real','natural','vintage'],
 ARRAY['bone','plastic','resin','synthetic'],
 ARRAY['iv0ry bangle','!vory bangle'],
 'Harrison et al. 2016', 'verified'),

('live pangolin', 'en', 3, 'pangolin_live', 0.91,
 ARRAY['sell','for sale','price','ship'],
 ARRAY['zoo','rescue','sanctuary'],
 ARRAY['l1ve pangolin','live p4ngolin'],
 'Challender et al. 2019', 'verified'),

('tiger skin rug', 'en', 9, 'tiger_skin', 0.94,
 '{}',
 ARRAY['faux','faux fur','synthetic'],
 ARRAY['t!ger skin rug','tiger sk1n rug'],
 'EIA 2019', 'verified'),

-- ============================================================
-- CHINESE (zh) — ~15 entries
-- ============================================================

('象牙', 'zh', 1, 'ivory_raw', 0.95,
 '{}',
 ARRAY['博物馆','展览','仿制品'],
 ARRAY['象牙.','象_牙','象丫','象☆牙'],
 'TRAFFIC China 2017', 'verified'),

('犀牛角', 'zh', 7, 'rhino_horn', 0.97,
 '{}',
 ARRAY['博物馆','仿制品'],
 ARRAY['犀.牛.角','犀牛角粉','犀_牛_角'],
 'Milliken & Shaw 2012', 'verified'),

('犀角粉', 'zh', 7, 'rhino_horn_powder', 0.95,
 ARRAY['药','保健'],
 ARRAY['合成','仿品'],
 ARRAY['犀.角.粉','犀角_粉'],
 'Xu et al. 2020', 'verified'),

('穿山甲', 'zh', 3, 'pangolin_scales', 0.92,
 '{}',
 ARRAY['模型','标本','研究'],
 ARRAY['穿.山.甲','穿山_甲','穿山甲片'],
 'Challender et al. 2019', 'verified'),

('穿山甲鳞片', 'zh', 3, 'pangolin_scales', 0.94,
 '{}',
 ARRAY['标本','教学'],
 ARRAY['穿山甲_鳞片','鳞.片'],
 'TRAFFIC China 2017', 'verified'),

('虎骨', 'zh', 9, 'tiger_bone', 0.96,
 '{}',
 ARRAY['假','仿制'],
 ARRAY['虎.骨','虎_骨','虎0骨'],
 'EIA 2019', 'verified'),

('虎骨酒', 'zh', 9, 'tiger_bone_wine', 0.93,
 '{}',
 ARRAY['虎骨风湿酒（合法）'],
 ARRAY['虎.骨.酒','虎_骨_酒'],
 'EIA 2019', 'verified'),

('熊胆', 'zh', 21, 'bear_bile', 0.94,
 ARRAY['药','胶囊','粉'],
 ARRAY['合成熊去氧胆酸','UDCA'],
 ARRAY['熊.胆','熊_胆','熊0胆'],
 'Animals Asia 2018', 'verified'),

('熊胆粉', 'zh', 21, 'bear_bile_powder', 0.92,
 ARRAY['药','保健'],
 ARRAY['合成','人工'],
 ARRAY['熊胆_粉','熊.胆.粉'],
 'Animals Asia 2018', 'verified'),

('海马', 'zh', 28, 'seahorse_dried', 0.88,
 ARRAY['药','补肾','干'],
 ARRAY['水族箱','观赏','合法贸易证'],
 ARRAY['海.马','海_马','h4im4'],
 'Project Seahorse 2018', 'verified'),

('玳瑁', 'zh', 10, 'tortoiseshell', 0.90,
 ARRAY['手镯','梳子','装饰'],
 ARRAY['仿制品','塑料','树脂'],
 ARRAY['玳.瑁','玳_瑁','d4im4o'],
 'Lyons et al. 2017', 'verified'),

('盔犀鸟', 'zh', 14, 'hornbill_casque', 0.91,
 ARRAY['头骨','雕刻','出售'],
 ARRAY['动物园','保护区'],
 ARRAY['盔.犀.鸟','盔犀_鸟'],
 'EIA 2015', 'verified'),

('麝香', 'zh', 42, 'musk_pod', 0.86,
 ARRAY['天然','药','香水'],
 ARRAY['合成麝香','人工'],
 ARRAY['麝.香','麝_香','shexiang'],
 'TRAFFIC China 2017', 'verified'),

('沉香木', 'zh', 26, 'rosewood_log', 0.70,
 ARRAY['原木','出售','大料'],
 ARRAY['人工种植','证书','合法'],
 ARRAY['沉.香.木','沉香_木'],
 'Forest Trends 2019', 'verified'),

('鱼翅', 'zh', 23, 'shark_fin', 0.87,
 ARRAY['出售','批发','整箱'],
 ARRAY['餐厅菜单','合法进口'],
 ARRAY['鱼.翅','鱼_翅','y4ch4'],
 'Dent & Clarke 2015', 'verified'),

-- ============================================================
-- INDONESIAN (id) — ~10 entries
-- ============================================================

('gading gajah', 'id', 1, 'ivory_raw', 0.94,
 '{}',
 ARRAY['museum','pameran','replika'],
 ARRAY['gad1ng gajah','gading_gajah','g4d1ng'],
 'TRAFFIC Indonesia 2019', 'verified'),

('gading ukiran', 'id', 1, 'ivory_worked', 0.88,
 ARRAY['gajah','antik','jual'],
 ARRAY['plastik','resin','imitasi'],
 ARRAY['gad1ng ukiran','gading_ukiran'],
 'TRAFFIC Indonesia 2019', 'verified'),

('trenggiling hidup', 'id', 3, 'pangolin_live', 0.92,
 ARRAY['jual','harga','kirim'],
 ARRAY['kebun binatang','rehabilitasi'],
 ARRAY['trenggl1ng','trenggiling_hidup','tr3ngiling'],
 'Challender et al. 2019', 'verified'),

('sisik trenggiling', 'id', 3, 'pangolin_scales', 0.90,
 '{}',
 ARRAY['sampel penelitian','museum'],
 ARRAY['sisik_trenggiling','s1sik trenggiling'],
 'TRAFFIC Indonesia 2019', 'verified'),

('kulit ular sanca', 'id', 17, 'snake_skin', 0.84,
 ARRAY['jual','meter','lembaran'],
 ARRAY['kulit sintetis','vinil'],
 ARRAY['kulit_ular','kul1t ular s4nc4'],
 'Natuschke et al. 2018', 'verified'),

('tokek kering', 'id', 32, 'gecko_dried', 0.87,
 ARRAY['jual','obat','kilo'],
 ARRAY['mainan','dekorasi'],
 ARRAY['tok3k kering','tokek_kering','t0k3k'],
 'Nijman et al. 2021', 'verified'),

('tokek hidup', 'id', 32, 'gecko_live', 0.83,
 ARRAY['jual','harga','besar'],
 ARRAY['kebun binatang','penangkaran resmi'],
 ARRAY['tok3k hidup','t0kek hidup'],
 'Nijman et al. 2021', 'verified'),

('empedu beruang', 'id', 22, 'bear_bile', 0.89,
 ARRAY['obat','tradisional','kering'],
 ARRAY['sintetis','farmasi resmi'],
 ARRAY['empedu_beruang','3mpedu beruang','emped4 beruang'],
 'Animals Asia 2018', 'verified'),

('sirip hiu', 'id', 23, 'shark_fin', 0.86,
 ARRAY['jual','kering','kilo','grosir'],
 ARRAY['restoran resmi','impor legal'],
 ARRAY['sir1p hiu','sirip_hiu','s1r1p h1u'],
 'TRAFFIC SEAP 2020', 'verified'),

('akar bajakah', 'id', 26, 'rosewood_root', 0.68,
 ARRAY['kayu','jual','gelondongan'],
 ARRAY['legal','izin','bersertifikat'],
 ARRAY['akar_bajakah','4kar b4j4kah'],
 'Forest Trends 2019', 'verified'),

-- ============================================================
-- ADDITIONAL ENTRIES — mixed languages to reach ~100
-- ============================================================

-- Thai extras
('เขี้ยวเสือ', 'th', 9, 'tiger_tooth', 0.88,
 ARRAY['เครื่องราง','ขาย'],
 ARRAY['ปลอม','เรซิน'],
 ARRAY['เขี้ยว.เสือ','kh14osuea'],
 'EIA Thailand 2020', 'verified'),

('ตับหมีสด', 'th', 22, 'bear_organ', 0.80,
 ARRAY['ยา','สด'],
 ARRAY['หมูป่า','วัว'],
 ARRAY['ตับหมี.สด','t4b_hm1_s0d'],
 'Animals Asia 2018', 'verified'),

('กระดูกเสือดาว', 'th', 9, 'leopard_bone', 0.84,
 ARRAY['ยา','ดาว'],
 ARRAY['สัตว์อื่น','ปลอม'],
 ARRAY['กระดูก.เสือดาว'],
 'EIA Thailand 2020', 'provisional'),

-- Vietnamese extras
('nanh hổ', 'vi', 9, 'tiger_tooth', 0.89,
 ARRAY['bùa','bán','thật'],
 ARRAY['nhựa','giả'],
 ARRAY['nanh_h0','n4nh h0'],
 'EIA Vietnam 2021', 'verified'),

('sừng tê một sừng', 'vi', 8, 'rhino_horn', 0.96,
 '{}',
 ARRAY['bảo tàng'],
 ARRAY['sung te m0t sung','s4ng_te_1_s4ng'],
 'ENV Vietnam 2020', 'verified'),

-- English extras
('tiger claw pendant', 'en', 9, 'tiger_claw', 0.86,
 ARRAY['genuine','real','natural'],
 ARRAY['metal','synthetic','replica'],
 ARRAY['t!ger claw','tiger cl4w pendant'],
 'EIA 2019', 'verified'),

('rhino horn bangle', 'en', 7, 'rhino_horn_worked', 0.91,
 '{}',
 ARRAY['replica','resin','acrylic'],
 ARRAY['rh!no horn bangle','rhin0_horn_bangle'],
 'Milliken & Shaw 2012', 'verified'),

('dried seahorse', 'en', 28, 'seahorse_dried', 0.87,
 ARRAY['bulk','wholesale','medicine','TCM'],
 ARRAY['aquarium display','souvenir replica'],
 ARRAY['dr13d seahorse','dried s3ahorse'],
 'Project Seahorse 2018', 'verified'),

-- Chinese extras
('虎牙', 'zh', 9, 'tiger_tooth', 0.91,
 ARRAY['挂件','真品','出售'],
 ARRAY['仿制','树脂','假'],
 ARRAY['虎.牙','虎_牙','h4y4'],
 'EIA 2019', 'verified'),

('犀牛皮', 'zh', 7, 'rhino_hide', 0.88,
 ARRAY['出售','制品'],
 ARRAY['仿制品','合成皮'],
 ARRAY['犀.牛.皮','犀牛_皮'],
 'TRAFFIC China 2017', 'verified'),

-- Indonesian extras
('tanduk badak', 'id', 7, 'rhino_horn', 0.95,
 '{}',
 ARRAY['museum','replika','hias'],
 ARRAY['t4nduk b4d4k','tanduk_badak','t@nduk b@d@k'],
 'TRAFFIC Indonesia 2019', 'verified'),

('kulit harimau', 'id', 9, 'tiger_skin', 0.93,
 '{}',
 ARRAY['sintetis','bulu imitasi'],
 ARRAY['kul1t harimau','kulit_harimau'],
 'TRAFFIC Indonesia 2019', 'verified'),

('tulang harimau', 'id', 9, 'tiger_bone', 0.90,
 ARRAY['obat','jual','kering'],
 ARRAY['sapi','sintetis'],
 ARRAY['tul4ng harimau','tulang_harimau'],
 'EIA 2019', 'verified'),

('paruh rangkong', 'id', 14, 'hornbill_casque', 0.92,
 ARRAY['jual','ukiran'],
 ARRAY['plastik','replika'],
 ARRAY['paruh_rangkong','p4ruh r4ngkong'],
 'EIA 2015', 'verified'),

('cula badak', 'id', 8, 'rhino_horn', 0.96,
 '{}',
 ARRAY['museum','replika'],
 ARRAY['cul4 b4d4k','cula_badak','cul@ b@d@k'],
 'TRAFFIC Indonesia 2019', 'verified');
