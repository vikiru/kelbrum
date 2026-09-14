type MetaAttribute = 'name' | 'property';

export function updateDocumentMetaTags(title: string, description: string) {
  document.title = title;
  setMetaContent('name', 'description', description);
  setMetaContent('property', 'og:title', title);
  setMetaContent('property', 'og:description', description);
  setMetaContent('name', 'twitter:title', title);
  setMetaContent('name', 'twitter:description', description);
}

function setMetaContent(attribute: MetaAttribute, value: string, content: string) {
  let element = document.head.querySelector<HTMLMetaElement>(`meta[${attribute}="${value}"]`);
  if (!element) {
    element = document.createElement('meta');
    element.setAttribute(attribute, value);
    document.head.append(element);
  }
  element.content = content;
}
