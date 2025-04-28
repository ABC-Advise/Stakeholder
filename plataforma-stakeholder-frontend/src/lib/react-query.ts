import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: 1, // Limita o número de tentativas em caso de erro
            staleTime: 1000 * 60 * 5, // Cache por 5 minutos
            cacheTime: 1000 * 60 * 30, // Mantém o cache por 30 minutos
            refetchOnWindowFocus: false, // Não refaz a requisição quando a janela ganha foco
            refetchOnReconnect: false, // Não refaz a requisição quando reconecta
        },
    },
})
