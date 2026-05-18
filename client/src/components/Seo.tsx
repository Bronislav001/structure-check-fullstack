import React, { useEffect } from 'react'

type Props = {
  title: string
  description: string
  canonicalPath?: string
  robots?: string
  ogType?: string
  jsonLd?: Record<string, any> | Record<string, any>[]
}

function upsertMeta(selector: string, create: () => HTMLMetaElement, set: (el: HTMLMetaElement) => void) {
  let el = document.head.querySelector(selector) as HTMLMetaElement | null
  if (!el) {
    el = create()
    document.head.appendChild(el)
  }
  set(el)
}

export default function Seo({ title, description, canonicalPath = '/', robots = 'index,follow', ogType = 'website', jsonLd }: Props) {
  useEffect(() => {
    const siteName = 'Struct Check'
    const finalTitle = title.includes(siteName) ? title : `${title} — ${siteName}`
    const origin = window.location.origin
    const canonicalUrl = `${origin}${canonicalPath}`

    document.title = finalTitle

    upsertMeta('meta[name="description"]', () => {
      const el = document.createElement('meta')
      el.name = 'description'
      return el
    }, (el) => {
      el.setAttribute('content', description)
    })

    upsertMeta('meta[name="robots"]', () => {
      const el = document.createElement('meta')
      el.name = 'robots'
      return el
    }, (el) => {
      el.setAttribute('content', robots)
    })

    upsertMeta('meta[property="og:title"]', () => {
      const el = document.createElement('meta')
      el.setAttribute('property', 'og:title')
      return el
    }, (el) => {
      el.setAttribute('content', finalTitle)
    })

    upsertMeta('meta[property="og:description"]', () => {
      const el = document.createElement('meta')
      el.setAttribute('property', 'og:description')
      return el
    }, (el) => {
      el.setAttribute('content', description)
    })

    upsertMeta('meta[property="og:type"]', () => {
      const el = document.createElement('meta')
      el.setAttribute('property', 'og:type')
      return el
    }, (el) => {
      el.setAttribute('content', ogType)
    })

    upsertMeta('meta[property="og:url"]', () => {
      const el = document.createElement('meta')
      el.setAttribute('property', 'og:url')
      return el
    }, (el) => {
      el.setAttribute('content', canonicalUrl)
    })

    let canonical = document.head.querySelector('link[rel="canonical"]') as HTMLLinkElement | null
    if (!canonical) {
      canonical = document.createElement('link')
      canonical.rel = 'canonical'
      document.head.appendChild(canonical)
    }
    canonical.href = canonicalUrl

    const scriptId = 'seo-jsonld'
    const oldScript = document.getElementById(scriptId)
    if (oldScript) oldScript.remove()

    if (jsonLd) {
      const script = document.createElement('script')
      script.id = scriptId
      script.type = 'application/ld+json'
      script.text = JSON.stringify(jsonLd)
      document.head.appendChild(script)
    }

    return () => {
      const current = document.getElementById(scriptId)
      if (current) current.remove()
    }
  }, [title, description, canonicalPath, robots, ogType, jsonLd])

  return null
}
