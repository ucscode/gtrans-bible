package com.ucscode.gtransbible.ads

import android.app.Activity
import android.app.Application
import android.os.Bundle
import com.ucscode.gtransbible.ui.MainActivity

class BibleApplication : Application(), Application.ActivityLifecycleCallbacks {
    lateinit var adsController: AdsController
        private set

    override fun onCreate() {
        super.onCreate()
        adsController = AdsController(this)
        registerActivityLifecycleCallbacks(this)
    }

    override fun onActivityCreated(activity: Activity, savedInstanceState: Bundle?) {
        if (activity is MainActivity) adsController.onActivityCreated(activity)
    }

    override fun onActivityStarted(activity: Activity) {
        if (activity is MainActivity) adsController.onActivityStarted(activity)
    }

    override fun onActivityResumed(activity: Activity) {
        if (activity is MainActivity) adsController.onActivityResumed(activity)
    }

    override fun onActivityPaused(activity: Activity) {
        if (activity is MainActivity) adsController.onActivityPaused(activity)
    }

    override fun onActivityStopped(activity: Activity) {
        if (activity is MainActivity) adsController.onActivityStopped(activity)
    }

    override fun onActivitySaveInstanceState(activity: Activity, outState: Bundle) = Unit

    override fun onActivityDestroyed(activity: Activity) {
        if (activity is MainActivity) adsController.onActivityDestroyed(activity)
    }
}
