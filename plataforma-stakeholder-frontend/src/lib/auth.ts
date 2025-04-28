import NextAuth, { getServerSession, NextAuthOptions } from 'next-auth'
import GoogleProvider from 'next-auth/providers/google'
import { setCookie } from 'nookies'

export const authOptions: NextAuthOptions = {
  pages: {
    signIn: '/auth/sign-in',
    error: '/auth/error',
  },
  session: {
    strategy: 'jwt',
  },
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID ?? '',
      clientSecret: process.env.GOOGLE_CLIENT_SECRET ?? '',
    }),
  ],
  callbacks: {
    // async signIn({ user }) {
    //   // Lista de emails e domínios permitidos
    //   const allowedEmails = ['miguellemes005@gmail.com']
    //   const allowedDomains = ['@abcadvise.com.br', '@infinitfy.com']

    //   if (user.email) {
    //     // Verifica se o email é permitido ou possui um domínio permitido
    //     const isAllowedEmail = allowedEmails.includes(user.email)
    //     const isAllowedDomain = allowedDomains.some((domain) =>
    //       user?.email?.endsWith(domain),
    //     )

    //     if (isAllowedEmail || isAllowedDomain) {
    //       return true
    //     }
    //   }

    //   return false
    // },
    async signIn({ user }) {
      // Verifica se o email do usuário possui o domínio permitido
      if (
        user.email &&
        (user.email === 'miguellemes005@gmail.com' ||
          user.email === 'waltagan@gmail.com' ||
          user.email === 'infinitfy.sergiomelges@gmail.com' ||
          user.email === 'danielgcmenezes2021@gmail.com')
      ) {
        return true
      } else {
        // Bloqueia o acesso se o domínio não for permitido
        return false
      }
    },
    async jwt({ token, user, account }) {
      if (account && user) {
        return {
          ...token,
          id: user.id,
          accessToken: account.access_token,
          idToken: account.id_token,
        }
      }

      return token
    },
    async session({ session, token }) {
      return {
        ...session,
        user: {
          ...session.user,
          id: token.id,
          type: token.type,
          accessToken: token.accessToken,
          idToken: token.idToken,
        },
      }
    },
  },
  debug: true,
  secret: process.env.NEXTAUTH_SECRET,
}
