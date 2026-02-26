# FlowDroid TaintBench 分析结果综合表格

## 配置说明

- **1x**: 原始超时设置 (CT=600s, DT=1800s, RT=120s)
- **✓**: 成功
- **✗ (-9)**: 失败 (内存不足, SIGKILL)
- **○ (黑名单)**: 已跳过

| APK | APK 路径 | Full (1x) | ne (1x) | ns (1x) | ne_ns (1x) |
|-----|----------|-----------|---------|---------|------------|
| backflash | `~/LDFA-dataset/TaintBench/apks/backflash.apk` | ✓ | ✓ | ✓ | ✓ |
| beita_com_beita_contact | `~/LDFA-dataset/TaintBench/apks/beita_com_beita_contact.apk` | ✓ | ✓ | ✓ | ✓ |
| cajino_baidu | `~/LDFA-dataset/TaintBench/apks/cajino_baidu.apk` | ○ (黑名单) | ○ (黑名单) | ○ (黑名单) | ○ (黑名单) |
| chat_hook | `~/LDFA-dataset/TaintBench/apks/chat_hook.apk` | ✓ | ✓ | ✓ | ✓ |
| chulia | `~/LDFA-dataset/TaintBench/apks/chulia.apk` | ✓ | ✓ | ✓ | ✓ |
| death_ring_materialflow | `~/LDFA-dataset/TaintBench/apks/death_ring_materialflow.apk` | ○ (黑名单) | ○ (黑名单) | ○ (黑名单) | ○ (黑名单) |
| dsencrypt_samp | `~/LDFA-dataset/TaintBench/apks/dsencrypt_samp.apk` | ✓ | ✓ | ✓ | ✓ |
| exprespam | `~/LDFA-dataset/TaintBench/apks/exprespam.apk` | ✓ | ✓ | ✓ | ✓ |
| fakeappstore | `~/LDFA-dataset/TaintBench/apks/fakeappstore.apk` | ✓ | ✓ | ✓ | ✓ |
| fakebank_android_samp | `~/LDFA-dataset/TaintBench/apks/fakebank_android_samp.apk` | ✓ | ✓ | ✓ | ✓ |
| fakedaum | `~/LDFA-dataset/TaintBench/apks/fakedaum.apk` | ✓ | ✓ | ✓ | ✓ |
| fakemart | `~/LDFA-dataset/TaintBench/apks/fakemart.apk` | ✓ | ✓ | ✓ | ✓ |
| fakeplay | `~/LDFA-dataset/TaintBench/apks/fakeplay.apk` | ✓ | ✓ | ✓ | ✓ |
| faketaobao | `~/LDFA-dataset/TaintBench/apks/faketaobao.apk` | ✓ | ✓ | ✓ | ✓ |
| godwon_samp | `~/LDFA-dataset/TaintBench/apks/godwon_samp.apk` | ✓ | ✓ | ✓ | ✓ |
| hummingbad_android_samp | `~/LDFA-dataset/TaintBench/apks/hummingbad_android_samp.apk` | ○ (黑名单) | ○ (黑名单) | ○ (黑名单) | ○ (黑名单) |
| jollyserv | `~/LDFA-dataset/TaintBench/apks/jollyserv.apk` | ○ (黑名单) | ○ (黑名单) | ○ (黑名单) | ○ (黑名单) |
| overlay_android_samp | `~/LDFA-dataset/TaintBench/apks/overlay_android_samp.apk` | ✓ | ✓ | ✓ | ✓ |
| overlaylocker2_android_samp | `~/LDFA-dataset/TaintBench/apks/overlaylocker2_android_samp.apk` | ✓ | ✓ | ✓ | ✓ |
| phospy | `~/LDFA-dataset/TaintBench/apks/phospy.apk` | ✓ | ✓ | ✓ | ✓ |
| proxy_samp | `~/LDFA-dataset/TaintBench/apks/proxy_samp.apk` | ✓ | ✓ | ✓ | ✓ |
| remote_control_smack | `~/LDFA-dataset/TaintBench/apks/remote_control_smack.apk` | ✗ (-9) | ○ (黑名单) | ○ (黑名单) | ○ (黑名单) |
| repane | `~/LDFA-dataset/TaintBench/apks/repane.apk` | ✓ | ✓ | ✓ | ✓ |
| roidsec | `~/LDFA-dataset/TaintBench/apks/roidsec.apk` | ✓ | ✓ | ✓ | ✓ |
| samsapo | `~/LDFA-dataset/TaintBench/apks/samsapo.apk` | ✓ | ✓ | ✓ | ✓ |
| save_me | `~/LDFA-dataset/TaintBench/apks/save_me.apk` | ✓ | ✓ | ✓ | ✓ |
| scipiex | `~/LDFA-dataset/TaintBench/apks/scipiex.apk` | ✗ (-9) | ○ (黑名单) | ○ (黑名单) | ○ (黑名单) |
| slocker_android_samp | `~/LDFA-dataset/TaintBench/apks/slocker_android_samp.apk` | ✓ | ✓ | ✓ | ✓ |
| sms_google | `~/LDFA-dataset/TaintBench/apks/sms_google.apk` | ✓ | ✓ | ✓ | ✓ |
| sms_send_locker_qqmagic | `~/LDFA-dataset/TaintBench/apks/sms_send_locker_qqmagic.apk` | ✓ | ✓ | ✓ | ✓ |
| smssend_packageInstaller | `~/LDFA-dataset/TaintBench/apks/smssend_packageInstaller.apk` | ✓ | ✓ | ✓ | ✓ |
| smssilience_fake_vertu | `~/LDFA-dataset/TaintBench/apks/smssilience_fake_vertu.apk` | ✓ | ✓ | ✓ | ✓ |
| smsstealer_kysn_assassincreed_android_samp | `~/LDFA-dataset/TaintBench/apks/smsstealer_kysn_assassincreed_android_samp.apk` | ✓ | ✓ | ✓ | ✓ |
| stels_flashplayer_android_update | `~/LDFA-dataset/TaintBench/apks/stels_flashplayer_android_update.apk` | ✓ | ✓ | ✓ | ✓ |
| tetus | `~/LDFA-dataset/TaintBench/apks/tetus.apk` | ✓ | ✓ | ✓ | ✓ |
| the_interview_movieshow | `~/LDFA-dataset/TaintBench/apks/the_interview_movieshow.apk` | ✓ | ✓ | ✓ | ✓ |
| threatjapan_uracto | `~/LDFA-dataset/TaintBench/apks/threatjapan_uracto.apk` | ✓ | ✓ | ✓ | ✓ |
| vibleaker_android_samp | `~/LDFA-dataset/TaintBench/apks/vibleaker_android_samp.apk` | ✗ (-9) | ○ (黑名单) | ○ (黑名单) | ○ (黑名单) |
| xbot_android_samp | `~/LDFA-dataset/TaintBench/apks/xbot_android_samp.apk` | ✗ (-9) | ✗ (-9) | ✗ (-9) | ✗ (-9) |