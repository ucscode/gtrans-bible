package com.ucscode.gtransbible.ads

import android.app.Activity
import android.content.Context
import android.util.Log
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.widget.FrameLayout
import androidx.core.content.edit
import com.google.android.gms.ads.AdError
import com.google.android.gms.ads.AdListener
import com.google.android.gms.ads.AdRequest
import com.google.android.gms.ads.AdSize
import com.google.android.gms.ads.LoadAdError
import com.google.android.gms.ads.MobileAds
import com.google.android.gms.ads.appopen.AppOpenAd
import com.google.android.gms.ads.appopen.AppOpenAd.AppOpenAdLoadCallback
import com.google.android.gms.ads.FullScreenContentCallback
import com.google.android.gms.ads.AdView
import com.google.android.ump.ConsentInformation
import com.google.android.ump.ConsentRequestParameters
import com.google.android.ump.UserMessagingPlatform
import com.ucscode.gtransbible.BuildConfig
import com.ucscode.gtransbible.R
import com.ucscode.gtransbible.ui.MainActivity

class AdsController(context: Context) {
    private val applicationContext = context.applicationContext
    private val preferences = applicationContext.getSharedPreferences(ADS_PREFERENCES, Context.MODE_PRIVATE)
    private val consentInformation = UserMessagingPlatform.getConsentInformation(applicationContext)

    var adsEnabled: Boolean = true
        set(value) {
            if (field == value) return
            field = value
            refreshAdsForCurrentState()
        }

    private var consentAllowsAds = false
    private var consentRequestStarted = false
    private var mobileAdsInitializationStarted = false
    private var mobileAdsInitialized = false
    private var firstEverLaunchPending = false
    private var configurationTransitionPending = false
    private var startedActivityCount = 0
    private var backgroundedAtMs: Long? = null
    private var currentActivity: MainActivity? = null
    private var currentPlacement = AdPlacement.NONE
    private var bannerView: AdView? = null
    private var bannerLoaded = false
    private var bannerLoadPending = false
    private var appOpenAd: AppOpenAd? = null
    private var appOpenLoadedAtMs = 0L
    private var appOpenLoading = false
    private var appOpenShowing = false

    init {
        firstEverLaunchPending = !preferences.getBoolean(KEY_HAS_LAUNCHED, false)
        if (firstEverLaunchPending) preferences.edit { putBoolean(KEY_HAS_LAUNCHED, true) }
        if (BuildConfig.ADMOB_MODE == MODE_TEST) Log.i(TAG, "AdMob mode: TEST")
    }

    fun onActivityCreated(activity: MainActivity) {
        currentActivity = activity
        if (consentRequestStarted) return
        consentRequestStarted = true
        consentInformation.requestConsentInfoUpdate(
            activity,
            ConsentRequestParameters.Builder().build(),
            {
                updatePrivacyOptionsEntryPoint()
                presentConsentFormIfRequired()
                // UMP permits ad requests when its cached consent state already allows them.
                refreshConsentAndAds()
            },
            { error ->
                Log.w(TAG, "Consent information update failed; app remains usable: ${error.message}")
                updatePrivacyOptionsEntryPoint()
                refreshConsentAndAds()
            },
        )
        // Do not block the Bible UI while UMP refreshes consent information.
        refreshConsentAndAds()
    }

    fun onActivityStarted(activity: MainActivity) {
        currentActivity = activity
        if (startedActivityCount == 0) {
            if (configurationTransitionPending) {
                configurationTransitionPending = false
            } else {
                val now = System.currentTimeMillis()
                val backgroundDuration = backgroundedAtMs?.let { (now - it).coerceAtLeast(0L) } ?: Long.MAX_VALUE
                val firstEverLaunch = firstEverLaunchPending
                firstEverLaunchPending = false
                tryShowAppOpen(backgroundDuration, firstEverLaunch, now)
                backgroundedAtMs = null
            }
        }
        startedActivityCount += 1
    }

    fun onActivityResumed(activity: MainActivity) {
        currentActivity = activity
        bannerView?.resume()
    }

    fun onActivityPaused(activity: MainActivity) {
        if (currentActivity === activity) bannerView?.pause()
    }

    fun onActivityStopped(activity: MainActivity) {
        startedActivityCount = (startedActivityCount - 1).coerceAtLeast(0)
        if (startedActivityCount == 0) {
            if (activity.isChangingConfigurations) {
                configurationTransitionPending = true
            } else {
                backgroundedAtMs = System.currentTimeMillis()
            }
        }
    }

    fun onActivityDestroyed(activity: MainActivity) {
        if (currentActivity !== activity) return
        removeBanner()
        currentActivity = null
    }

    fun setBannerPlacement(activity: MainActivity, placement: AdPlacement) {
        currentActivity = activity
        currentPlacement = placement
        if (!AdPolicy.allowsBanner(adsEnabled, placement) || !isAdRequestAllowed()) {
            removeBanner()
            return
        }
        attachBannerIfNeeded(activity)
    }

    fun showPrivacyOptions(activity: MainActivity) {
        if (consentInformation.privacyOptionsRequirementStatus != ConsentInformation.PrivacyOptionsRequirementStatus.REQUIRED) return
        UserMessagingPlatform.showPrivacyOptionsForm(activity) { formError ->
            if (formError != null) Log.w(TAG, "Privacy options form could not be shown")
            updatePrivacyOptionsEntryPoint()
            refreshConsentAndAds()
        }
    }

    private fun refreshConsentAndAds() {
        consentAllowsAds = runCatching { consentInformation.canRequestAds() }.getOrDefault(false)
        refreshAdsForCurrentState()
    }

    private fun presentConsentFormIfRequired() {
        val activity = currentActivity?.takeUnless { it.isFinishing || it.isDestroyed }
        if (activity == null) {
            refreshConsentAndAds()
            return
        }
        UserMessagingPlatform.loadAndShowConsentFormIfRequired(activity) { formError ->
            if (formError != null) Log.w(TAG, "Consent form unavailable; app remains usable")
            updatePrivacyOptionsEntryPoint()
            refreshConsentAndAds()
        }
    }

    private fun refreshAdsForCurrentState() {
        if (!isAdRequestAllowed()) {
            removeBanner()
            appOpenAd = null
            return
        }
        if (!mobileAdsInitializationStarted) {
            mobileAdsInitializationStarted = true
            MobileAds.initialize(applicationContext) {
                mobileAdsInitialized = true
                loadAppOpenAd()
                currentActivity?.let { setBannerPlacement(it, currentPlacement) }
            }
        } else if (mobileAdsInitialized) {
            loadAppOpenAd()
            currentActivity?.let { setBannerPlacement(it, currentPlacement) }
        }
    }

    private fun isAdRequestAllowed(): Boolean = adsEnabled && consentAllowsAds

    private fun attachBannerIfNeeded(activity: MainActivity) {
        val slot = activity.findViewById<FrameLayout>(R.id.bottomAdSlot) ?: return
        slot.visibility = if (AdPolicy.shouldShowBannerSlot(true, bannerLoaded)) View.VISIBLE else View.GONE
        if (bannerView != null || bannerLoadPending || !mobileAdsInitialized) return
        bannerLoadPending = true
        slot.post {
            bannerLoadPending = false
            if (currentActivity !== activity || !AdPolicy.allowsBanner(adsEnabled, currentPlacement) || !isAdRequestAllowed() || !mobileAdsInitialized) return@post
            val widthPx = slot.width.takeIf { it > 0 } ?: activity.resources.displayMetrics.widthPixels
            val widthDp = (widthPx / activity.resources.displayMetrics.density).toInt().coerceAtLeast(1)
            val adView = AdView(activity).apply {
                adUnitId = BuildConfig.ADMOB_BANNER_UNIT_ID
                setAdSize(AdSize.getCurrentOrientationAnchoredAdaptiveBannerAdSize(activity, widthDp))
                adListener = object : AdListener() {
                    override fun onAdLoaded() {
                        if (bannerView !== this@apply || !isAdRequestAllowed() || !AdPolicy.allowsBanner(adsEnabled, currentPlacement)) return
                        bannerLoaded = true
                        slot.visibility = View.VISIBLE
                        Log.d(TAG, "Banner ready at ${currentPlacement.name}")
                    }

                    override fun onAdFailedToLoad(error: LoadAdError) {
                        if (bannerView !== this@apply) return
                        Log.w(TAG, "Banner unavailable at ${currentPlacement.name}; app remains usable")
                        removeBanner()
                    }
                }
            }
            bannerView = adView
            bannerLoaded = false
            slot.removeAllViews()
            slot.addView(
                adView,
                FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT, Gravity.CENTER),
            )
            slot.visibility = View.GONE
            Log.d(TAG, "Requesting banner at ${currentPlacement.name}")
            adView.loadAd(AdRequest.Builder().build())
        }
    }

    private fun removeBanner() {
        bannerLoadPending = false
        val activity = currentActivity
        val slot = activity?.findViewById<FrameLayout>(R.id.bottomAdSlot)
        slot?.visibility = View.GONE
        slot?.removeAllViews()
        bannerView?.destroy()
        bannerView = null
        bannerLoaded = false
    }

    private fun loadAppOpenAd() {
        if (!isAdRequestAllowed() || !mobileAdsInitialized || appOpenLoading || appOpenAd != null) return
        appOpenLoading = true
        AppOpenAd.load(
            applicationContext,
            BuildConfig.ADMOB_APP_OPEN_UNIT_ID,
            AdRequest.Builder().build(),
            object : AppOpenAdLoadCallback() {
                override fun onAdLoaded(ad: AppOpenAd) {
                    appOpenLoading = false
                    appOpenAd = ad
                    appOpenLoadedAtMs = System.currentTimeMillis()
                }

                override fun onAdFailedToLoad(error: LoadAdError) {
                    appOpenLoading = false
                    appOpenAd = null
                    Log.w(TAG, "App Open ad unavailable; app remains usable")
                }
            },
        )
    }

    private fun tryShowAppOpen(backgroundDuration: Long, firstEverLaunch: Boolean, now: Long) {
        val ad = appOpenAd
        if (ad == null) {
            loadAppOpenAd()
            return
        }
        val lastShownAt = preferences.getLong(KEY_LAST_APP_OPEN_SHOWN, 0L)
        val freshAdLoaded = now - appOpenLoadedAtMs <= APP_OPEN_AD_MAX_AGE_MS
        if (!freshAdLoaded) {
            appOpenAd = null
            loadAppOpenAd()
            return
        }
        if (!AdPolicy.canShowAppOpen(
                adsEnabled = isAdRequestAllowed(),
                firstEverLaunch = firstEverLaunch,
                adLoaded = true,
                adAlreadyShowing = appOpenShowing,
                backgroundDurationMs = backgroundDuration,
                lastShownAtMs = lastShownAt,
                nowMs = now,
            )
        ) return
        val activity = currentActivity ?: return
        if (activity.isFinishing || activity.isDestroyed) return
        appOpenAd = null
        appOpenShowing = true
        ad.fullScreenContentCallback = object : FullScreenContentCallback() {
            override fun onAdShowedFullScreenContent() {
                preferences.edit { putLong(KEY_LAST_APP_OPEN_SHOWN, System.currentTimeMillis()) }
            }

            override fun onAdDismissedFullScreenContent() {
                appOpenShowing = false
                appOpenAd = null
                loadAppOpenAd()
            }

            override fun onAdFailedToShowFullScreenContent(error: AdError) {
                appOpenShowing = false
                appOpenAd = null
                Log.w(TAG, "App Open ad could not be shown; app remains usable")
                loadAppOpenAd()
            }
        }
        runCatching { ad.show(activity) }.onFailure {
            appOpenShowing = false
            appOpenAd = null
            Log.w(TAG, "App Open ad could not be shown; app remains usable")
            loadAppOpenAd()
        }
    }

    private fun updatePrivacyOptionsEntryPoint() {
        val required = runCatching {
            consentInformation.privacyOptionsRequirementStatus == ConsentInformation.PrivacyOptionsRequirementStatus.REQUIRED
        }.getOrDefault(false)
        currentActivity?.setPrivacyOptionsRequired(required)
    }

    private companion object {
        const val TAG = "BibleAds"
        const val MODE_TEST = "TEST"
        const val ADS_PREFERENCES = "advertising_preferences"
        const val KEY_HAS_LAUNCHED = "has_launched"
        const val KEY_LAST_APP_OPEN_SHOWN = "last_app_open_shown_at"
        const val APP_OPEN_AD_MAX_AGE_MS = 4 * 60 * 60 * 1000L
    }

}
