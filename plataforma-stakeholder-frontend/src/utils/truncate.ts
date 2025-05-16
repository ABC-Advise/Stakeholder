export function truncate(title: string, maxLength = 18) {
  return title.length > maxLength ? title.slice(0, maxLength) + '...' : title;
}
