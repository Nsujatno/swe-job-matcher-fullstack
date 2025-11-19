"use client";

import { useEffect } from "react";
import { useUser, useAuth } from "@clerk/nextjs";

export default function SyncUser() {
  const { user, isSignedIn } = useUser();
  const { getToken } = useAuth();

  useEffect(() => {
    if (!isSignedIn || !user) return;

    const sync = async () => {
      try {
        const token = await getToken();

        await fetch("http://localhost:8000/api/sync-user", {
          method: "POST",
          headers: { 
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}` 
          },
        });
      } catch (err) {
        console.error("Failed to sync user", err);
      }
    };

    sync();
  }, [isSignedIn, user, getToken]);

  return null;
}