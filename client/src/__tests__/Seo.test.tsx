import { render } from '@testing-library/react'
import Seo from '../components/Seo'

describe('Seo', () => {
  it('writes meta tags and canonical link into head', () => {
    render(<Seo title="Главная" description="Описание" canonicalPath="/" robots="index,follow" jsonLd={{ '@context': 'https://schema.org', '@type': 'WebSite', name: 'Struct Check' }} />)

    expect(document.title).toContain('Главная')
    expect(document.head.querySelector('meta[name="description"]')?.getAttribute('content')).toBe('Описание')
    expect(document.head.querySelector('meta[name="robots"]')?.getAttribute('content')).toBe('index,follow')
    expect(document.head.querySelector('link[rel="canonical"]')?.getAttribute('href')).toContain('/')
    expect(document.getElementById('seo-jsonld')?.textContent).toContain('Struct Check')
  })
})
