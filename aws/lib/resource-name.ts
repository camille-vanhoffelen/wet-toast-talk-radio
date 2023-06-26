export function resourceName(name: string, dev?: boolean | undefined): string {
    if (dev) {
        return `${name}-dev`;
    }
    return name;
}
