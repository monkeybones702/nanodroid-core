## Crash Details

**Crash Thread**: `Thread[main,5,main]`  
**Crash Timestamp**: `2026-09-27 06:33:43.966 UTC`  

**Crash Message**:
```
The content of the adapter has changed but ListView did not receive a notification. Make sure the content of your adapter is not modified from a background thread, but only from the UI thread. Make sure your adapter calls notifyDataSetChanged() when its content changes. [in ListView(2131231117, class android.widget.ListView) with Adapter(class com.termux.app.terminal.TermuxSessionsListViewController)]
```


### Stacktrace

```
java.lang.IllegalStateException: The content of the adapter has changed but ListView did not receive a notification. Make sure the content of your adapter is not modified from a background thread, but only from the UI thread. Make sure your adapter calls notifyDataSetChanged() when its content changes. [in ListView(2131231117, class android.widget.ListView) with Adapter(class com.termux.app.terminal.TermuxSessionsListViewController)]
	at android.widget.ListView.layoutChildren(ListView.java:1892)
	at android.widget.AbsListView.onTouchUp(AbsListView.java:4890)
	at android.widget.AbsListView.onTouchEvent(AbsListView.java:4625)
	at android.widget.ListView.onTouchEvent(ListView.java:1787)
	at android.view.View.performOnTouchCallback(View.java:17597)
	at android.view.View.dispatchTouchEvent(View.java:17550)
	at android.view.ViewGroup.dispatchTransformedTouchEvent(ViewGroup.java:3452)
	at android.view.ViewGroup.dispatchTouchEvent(ViewGroup.java:3119)
	at android.widget.AbsListView.dispatchTouchEvent(AbsListView.java:11566)
	at android.view.ViewGroup.dispatchTransformedTouchEvent(ViewGroup.java:3458)
	at android.view.ViewGroup.dispatchTouchEvent(ViewGroup.java:3134)
	at android.view.ViewGroup.dispatchTransformedTouchEvent(ViewGroup.java:3458)
	at android.view.ViewGroup.dispatchTouchEvent(ViewGroup.java:3134)
	at android.view.ViewGroup.dispatchTransformedTouchEvent(ViewGroup.java:3458)
	at android.view.ViewGroup.dispatchTouchEvent(ViewGroup.java:3134)
	at android.view.ViewGroup.dispatchTransformedTouchEvent(ViewGroup.java:3458)
	at android.view.ViewGroup.dispatchTouchEvent(ViewGroup.java:3134)
	at android.view.ViewGroup.dispatchTransformedTouchEvent(ViewGroup.java:3458)
	at android.view.ViewGroup.dispatchTouchEvent(ViewGroup.java:3134)
	at android.view.ViewGroup.dispatchTransformedTouchEvent(ViewGroup.java:3458)
	at android.view.ViewGroup.dispatchTouchEvent(ViewGroup.java:3134)
	at android.view.ViewGroup.dispatchTransformedTouchEvent(ViewGroup.java:3458)
	at android.view.ViewGroup.dispatchTouchEvent(ViewGroup.java:3134)
	at com.android.internal.policy.DecorView.superDispatchTouchEvent(DecorView.java:1209)
	at com.android.internal.policy.PhoneWindow.superDispatchTouchEvent(PhoneWindow.java:2278)
	at android.app.Activity.dispatchTouchEvent(Activity.java:4925)
	at com.android.internal.policy.DecorView.dispatchTouchEvent(DecorView.java:1147)
	at android.view.View.dispatchPointerEvent(View.java:17887)
	at android.view.ViewRootImpl$ViewPostImeInputStage.processPointerEvent(ViewRootImpl.java:9950)
	at android.view.ViewRootImpl$ViewPostImeInputStage.onProcess(ViewRootImpl.java:9661)
	at android.view.ViewRootImpl$InputStage.deliver(ViewRootImpl.java:8994)
	at android.view.ViewRootImpl$InputStage.onDeliverToNext(ViewRootImpl.java:9051)
	at android.view.ViewRootImpl$InputStage.forward(ViewRootImpl.java:9017)
	at android.view.ViewRootImpl$AsyncInputStage.forward(ViewRootImpl.java:9222)
	at android.view.ViewRootImpl$InputStage.apply(ViewRootImpl.java:9025)
	at android.view.ViewRootImpl$AsyncInputStage.apply(ViewRootImpl.java:9279)
	at android.view.ViewRootImpl$InputStage.deliver(ViewRootImpl.java:8998)
	at android.view.ViewRootImpl$InputStage.onDeliverToNext(ViewRootImpl.java:9051)
	at android.view.ViewRootImpl$InputStage.forward(ViewRootImpl.java:9017)
	at android.view.ViewRootImpl$InputStage.apply(ViewRootImpl.java:9025)
	at android.view.ViewRootImpl$InputStage.deliver(ViewRootImpl.java:8998)
	at android.view.ViewRootImpl.deliverInputEvent(ViewRootImpl.java:12916)
	at android.view.ViewRootImpl.doProcessInputEvents(ViewRootImpl.java:12804)
	at android.view.ViewRootImpl.enqueueInputEvent(ViewRootImpl.java:12759)
	at android.view.ViewRootImpl.processRawInputEvent(ViewRootImpl.java:13274)
	at android.view.ViewRootImpl$WindowInputEventReceiver.onInputEvent(ViewRootImpl.java:13052)
	at android.view.InputEventReceiver.dispatchInputEvent(InputEventReceiver.java:369)
	at android.os.MessageQueue.nativePollOnce(Native Method)
	at android.os.MessageQueue.nextLegacy(MessageQueue.java:985)
	at android.os.MessageQueue.next(MessageQueue.java:1094)
	at android.os.Looper.loopOnce(Looper.java:222)
	at android.os.Looper.loop(Looper.java:392)
	at android.app.ActivityThread.main(ActivityThread.java:10346)
	at java.lang.reflect.Method.invoke(Native Method)
	at com.android.internal.os.RuntimeInit$MethodAndArgsCaller.run(RuntimeInit.java:638)
	at com.android.internal.os.ZygoteInit.main(ZygoteInit.java:972)

```
##


## Termux App Info

**APP_NAME**: `Termux`  
**PACKAGE_NAME**: `com.termux`  
**VERSION_NAME**: `0.118.3`  
**VERSION_CODE**: `1002`  
**TARGET_SDK**: `28`  
**IS_DEBUGGABLE_BUILD**: `true`  
**SE_PROCESS_CONTEXT**: `u:r:untrusted_app_27:s0:c96,c257,c512,c768`  
**SE_FILE_CONTEXT**: `u:object_r:app_data_file:s0:c96,c257,c512,c768`  
**SE_INFO**: `default:targetSdkVersion=28:complete`  
**APK_RELEASE**: `Github`  
**SIGNING_CERTIFICATE_SHA256_DIGEST**: `B6DA01480EEFD5FBF2CD3771B8D1021EC791304BDD6C4BF41D3FAABAD48EE5E1`  
##


## Device Info

### Software

**OS_VERSION**: `5.15.189-android13-3-33503169`  
**SDK_INT**: `36`  
**RELEASE**: `16`  
**ID**: `BP4A.251205.006`  
**DISPLAY**: `BP4A.251205.006.S166VUDS9DZH1`  
**INCREMENTAL**: `S166VUDS9DZH1`  
**SECURITY_PATCH**: `2026-08-05`  
**IS_DEBUGGABLE**: `0`  
**IS_TREBLE_ENABLED**: `true`  
**TYPE**: `user`  
**TAGS**: `release-keys`  

### Hardware

**MANUFACTURER**: `samsung`  
**BRAND**: `samsung`  
**MODEL**: `SM-S166V`  
**PRODUCT**: `a16xtfn`  
**BOARD**: `s5e8535`  
**HARDWARE**: `s5e8535`  
**DEVICE**: `a16x`  
**SUPPORTED_ABIS**: `arm64-v8a, armeabi-v7a, armeabi`  
**SUPPORTED_32_BIT_ABIS**: `armeabi-v7a, armeabi`  
**SUPPORTED_64_BIT_ABIS**: `arm64-v8a`  
**PAGE_SIZE**: `4096`  
##
