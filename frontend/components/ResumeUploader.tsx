"use client";

import { useState, useRef, ChangeEvent, DragEvent, useEffect } from "react";
import {
	UploadCloud,
	FileText,
	X,
	CheckCircle,
	AlertCircle,
	Loader2,
	Search,
} from "lucide-react";
import { useAuth } from "@clerk/nextjs";
import JobResultCard from "./JobResultCard";

// --- Types ---
export interface MatchDetails {
	score: number;
	reason: string;
	evidence: string[];
	missing_skills: string[];
}

export interface JobMatch {
	company: string;
	role: string;
	location: string;
	link: string;
	match_details: MatchDetails;
}

type UploadStatus = "idle" | "uploading" | "analyzing" | "success" | "error";

export default function ResumeUploader() {
	const { getToken } = useAuth();
	const [file, setFile] = useState<File | null>(null);
	const [isDragging, setIsDragging] = useState(false);
	const [status, setStatus] = useState<UploadStatus>("idle");
	const [errorMessage, setErrorMessage] = useState<string>("");
	const [matches, setMatches] = useState<JobMatch[]>([]);

	// hidden input reference
	const fileInputRef = useRef<HTMLInputElement>(null);

	// Configuration
	const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
	const ALLOWED_TYPES = ["application/pdf"];

	// --- Helpers ---

	const validateFile = (file: File): boolean => {
		if (!ALLOWED_TYPES.includes(file.type)) {
			setErrorMessage("Only PDF files are allowed.");
			setStatus("error");
			return false;
		}
		if (file.size > MAX_FILE_SIZE) {
			setErrorMessage("File size must be less than 5MB.");
			setStatus("error");
			return false;
		}
		return true;
	};

	const handleFileSelect = (selectedFile: File) => {
		setErrorMessage("");
		setStatus("idle");
		if (validateFile(selectedFile)) {
			setFile(selectedFile);
		}
	};

	const resetState = () => {
		setFile(null);
		setMatches([]);
		setStatus("idle");
		setErrorMessage("");
		if (fileInputRef.current) fileInputRef.current.value = "";
	};

	// --- Polling Logic ---

	const pollForResults = async () => {
		// Switch status to analyzing so the UI shows we are waiting for AI
		setStatus("analyzing");

		const interval = setInterval(async () => {
			try {
				const freshToken = await getToken();

				if (!freshToken) {
					console.log("No token available");
					return;
				}
				const res = await fetch("http://localhost:8000/api/resume-status", {
					headers: { Authorization: `Bearer ${freshToken}` },
				});

				if (!res.ok) return; // standard retry if network blip

				const data = await res.json();

				if (data.status === "completed") {
					clearInterval(interval);
					setMatches(data.matches);
					setStatus("success");
				} else if (data.status === "failed") {
					clearInterval(interval);
					setErrorMessage("AI Analysis failed. Please try again.");
					setStatus("error");
				}
				// If status is "processing" or "pending", we do nothing and wait for next loop
			} catch (err) {
				console.error("Polling error", err);
				// Don't clear interval immediately on network error, allow retries
			}
		}, 5000); // Check every 5
	};

	// --- Event Handlers ---

	const onDragOver = (e: DragEvent<HTMLDivElement>) => {
		e.preventDefault();
		setIsDragging(true);
	};

	const onDragLeave = (e: DragEvent<HTMLDivElement>) => {
		e.preventDefault();
		setIsDragging(false);
	};

	const onDrop = (e: DragEvent<HTMLDivElement>) => {
		e.preventDefault();
		setIsDragging(false);
		if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
			handleFileSelect(e.dataTransfer.files[0]);
		}
	};

	const onFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
		if (e.target.files && e.target.files.length > 0) {
			handleFileSelect(e.target.files[0]);
		}
	};

	const handleUpload = async () => {
		if (!file) return;
		setStatus("uploading");

		try {
			const token = await getToken();

			if (!token) {
				setErrorMessage("Please sign in first.");
				setStatus("error");
				return;
			}

			const formData = new FormData();
			formData.append("file", file); // Make sure backend expects 'file'

			const response = await fetch("http://localhost:8000/api/upload-resume", {
				method: "POST",
				headers: { Authorization: `Bearer ${token}` },
				body: formData,
			});

			if (!response.ok) {
				throw new Error("Failed to upload resume");
			}

			// Upload successful, now start polling for AI results
			await pollForResults();
		} catch (error) {
			console.error(error);
			setStatus("error");
			setErrorMessage("Something went wrong uploading your resume.");
		}
	};

	// --- View 1: The Results List (Show this when we have matches) ---
	if (status === "success" && matches.length > 0) {
		return (
			<div className="w-full max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
				<div className="flex items-center justify-between mb-8">
					<h2 className="text-3xl font-bold text-white">Top Matches for You</h2>
					<button
						onClick={resetState}
						className="text-sm text-slate-400 hover:text-white underline"
					>
						Upload different resume
					</button>
				</div>

				<div className="grid gap-6">
					{matches.map((job, index) => (
						<JobResultCard key={index} job={job} />
					))}
				</div>
			</div>
		);
	}

	// --- View 2: The Upload Box (Default) ---
	return (
		<div className="w-full max-w-xl mx-auto">
			{/* Drop Zone */}
			<div
				className={`
          relative border-2 border-dashed rounded-2xl p-8 transition-all duration-300 ease-in-out text-center cursor-pointer
          ${
											isDragging
												? "border-indigo-500 bg-indigo-500/10"
												: "border-slate-700 bg-slate-800/50 hover:bg-slate-800"
										}
          ${status === "error" ? "border-red-500/50 bg-red-500/5" : ""}
        `}
				onDragOver={onDragOver}
				onDragLeave={onDragLeave}
				onDrop={onDrop}
				onClick={() => fileInputRef.current?.click()}
			>
				<input
					type="file"
					ref={fileInputRef}
					className="hidden"
					accept=".pdf"
					onChange={onFileInputChange}
				/>

				{/* IDLE STATE: No file selected */}
				{!file && (
					<div className="space-y-4">
						<div className="w-16 h-16 bg-slate-700/50 rounded-full flex items-center justify-center mx-auto text-indigo-400">
							<UploadCloud size={32} />
						</div>
						<div>
							<p className="text-lg font-semibold text-white">
								Click to upload or drag and drop
							</p>
							<p className="text-sm text-slate-400 mt-1">PDF (max 5MB)</p>
						</div>
					</div>
				)}

				{/* SELECTED STATE: File is present */}
				{file && (
					<div className="flex items-center justify-between bg-slate-700/50 p-4 rounded-xl border border-slate-600">
						<div className="flex items-center gap-3 overflow-hidden">
							<div className="p-2 bg-indigo-500/20 rounded-lg text-indigo-400">
								<FileText size={24} />
							</div>
							<div className="text-left min-w-0">
								<p className="text-sm font-medium text-white truncate max-w-[200px]">
									{file.name}
								</p>
								<p className="text-xs text-slate-400">
									{(file.size / 1024 / 1024).toFixed(2)} MB
								</p>
							</div>
						</div>

						{/* Only show Remove X if not currently processing */}
						{status !== "uploading" && status !== "analyzing" && (
							<button
								onClick={(e) => {
									e.stopPropagation();
									resetState();
								}}
								className="p-1.5 hover:bg-slate-600 rounded-full text-slate-400 hover:text-white transition-colors"
							>
								<X size={20} />
							</button>
						)}
					</div>
				)}
			</div>

			{/* Error Message */}
			{errorMessage && (
				<div className="flex items-center gap-2 mt-4 text-red-400 bg-red-400/10 p-3 rounded-lg text-sm border border-red-400/20">
					<AlertCircle size={16} />
					{errorMessage}
				</div>
			)}

			{/* Action Button / Loading State */}
			{file && (
				<button
					onClick={handleUpload}
					disabled={status === "uploading" || status === "analyzing"}
					className={`
            mt-6 w-full py-3.5 rounded-xl font-semibold transition-all flex items-center justify-center gap-2
            ${
													status === "uploading" || status === "analyzing"
														? "bg-slate-700 text-slate-300 cursor-not-allowed"
														: "bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg shadow-indigo-500/25"
												}
          `}
				>
					{status === "uploading" && (
						<>
							<Loader2 size={20} className="animate-spin" />
							Uploading PDF...
						</>
					)}

					{status === "analyzing" && (
						<>
							<Search size={20} className="animate-pulse" />
							Scanning Jobs & Matching...
						</>
					)}

					{status === "idle" && "Run Job Matcher"}
					{status === "error" && "Try Again"}
				</button>
			)}

			{/* Info Text during Analysis */}
			{status === "analyzing" && (
				<div className="mt-4 text-center animate-in fade-in">
					<p className="text-slate-400 text-sm">
						This usually takes about 30 seconds. <br />
						We are scraping live data from GitHub.
					</p>
				</div>
			)}
		</div>
	);
}
