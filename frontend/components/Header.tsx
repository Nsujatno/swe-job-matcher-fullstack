"use client";

import {
	SignInButton,
	SignUpButton,
	SignedIn,
	SignedOut,
	UserButton,
} from "@clerk/nextjs";
import SyncUser from "@/components/SyncUser";
import Link from "next/link";
import { LayoutDashboard, Plus } from "lucide-react";

export default function Header() {
	return (
		<header className="fixed top-0 w-full z-50 bg-slate-950/80 backdrop-blur-md border-b border-slate-800">
			<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
				<Link href="/" className="flex items-center gap-2 group">
					<span className="font-bold text-xl text-white tracking-tight group-hover:text-indigo-400 transition-colors">
						Swe Job Matcher
					</span>
				</Link>

				<div className="flex items-center gap-4">
					<SignedIn>
						<nav className="hidden md:flex items-center gap-1 mr-2">
							<Link href="/dashboard">
								<button className="text-slate-400 hover:text-white text-sm font-medium px-3 py-2 rounded-lg hover:bg-slate-800 transition-all flex items-center gap-2">
									<LayoutDashboard size={16} />
									Dashboard
								</button>
							</Link>
							<Link href="/upload-resume">
								<button className="text-slate-400 hover:text-white text-sm font-medium px-3 py-2 rounded-lg hover:bg-slate-800 transition-all flex items-center gap-2">
									<Plus size={16} />
									New Scan
								</button>
							</Link>
						</nav>
					</SignedIn>
					<SignedOut>
						<SignInButton>
							<button className="text-slate-300 hover:text-white font-medium text-sm px-4 py-2 rounded-lg hover:bg-slate-800 transition-all">
								Sign In
							</button>
						</SignInButton>

						<SignUpButton>
							<button className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm px-4 py-2 rounded-lg transition-all shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/40">
								Get Started
							</button>
						</SignUpButton>
					</SignedOut>

					<SignedIn>
						<SyncUser />
						<div className="pl-2 border-l border-slate-800">
							<UserButton
								appearance={{
									elements: {
										avatarBox:
											"h-9 w-9 ring-2 ring-slate-800 hover:ring-indigo-500 transition-all",
									},
								}}
							/>
						</div>
					</SignedIn>
				</div>
			</div>
		</header>
	);
}
