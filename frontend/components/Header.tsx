'use client'

import {
  SignInButton,
  SignUpButton,
  SignedIn,
  SignedOut,
  UserButton,
} from '@clerk/nextjs'
import SyncUser from '@/components/SyncUser'

export default function Header() {
  return (
    <header className="flex justify-end items-center p-4 gap-3 h-16 border-b border-white/10">
      <SignedOut>
        
        {/* Sign In Button */}
        <SignInButton>
          <button
            className="text-neutral-300 hover:text-white font-medium text-sm px-5 py-2.5 rounded-full border border-white/10 hover:border-white/20 hover:scale-105 transition-colors duration-200 cursor-pointer will-change-transform [backface-hidden] [-webkit-font-smoothing:subpixel-antialiased]"
          >
            Sign In
          </button>
        </SignInButton>

        {/* Sign Up Button */}
        <SignUpButton>
          <button
            className="bg-indigo-600 text-white rounded-full font-semibold text-sm px-6 py-2.5 cursor-pointer transition-all shadow-lg hover:shadow-indigo-500/25 hover:scale-105"
          >
            Sign Up
          </button>
        </SignUpButton>

      </SignedOut>

      <SignedIn>
        <SyncUser />
        <UserButton />
      </SignedIn>
    </header>
  )
}
