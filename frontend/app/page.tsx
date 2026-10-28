"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "./services/api";

export default function Home() {

  const router = useRouter();

  const [file, setFile] =
    useState<File | null>(null);

  const [loading, setLoading] =
    useState(false);

  const handleUpload = async () => {

    if (!file) return;

    setLoading(true);

    const formData = new FormData();

    formData.append(
      "file",
      file
    );

    try {

      const response =
        await api.post(
          "/upload",
          formData,
          {
            headers: {
              "Content-Type":
                "multipart/form-data",
            },
          }
        );

      localStorage.setItem(
        "analysis",
        JSON.stringify(
          response.data
        )
      );

      router.push(
        "/dashboard"
      );

    } catch (err) {

      console.error(
        "Upload failed:",
        err
      );

      alert(
        "Failed to analyze file. Please try again."
      );

    } finally {

      setLoading(false);

    }
  };

  return (

    <main
      className="
        min-h-screen
        flex
        flex-col
        items-center
        justify-center
        bg-gray-50
        px-4
      "
    >

      <div
        className="
          bg-white
          shadow-xl
          rounded-2xl
          p-10
          w-full
          max-w-lg
          flex
          flex-col
          items-center
          gap-8
        "
      >

        {/* Header */}

        <div className="text-center">

          <h1
            className="
              text-6xl
              font-extrabold
              text-gray-900
              mb-3
            "
          >
            Arkspace
          </h1>

          <p
            className="
              text-lg
              text-gray-600
            "
          >
            Multi-Agent Workplace Intelligence Platform
          </p>

        </div>

        {/* File Upload */}

        <div
          className="
            flex
            flex-col
            items-center
            gap-4
            w-full
          "
        >

          <label
            htmlFor="file-upload"
            className="
              cursor-pointer
              px-6
              py-3
              bg-blue-600
              text-white
              font-semibold
              rounded-lg
              shadow-md
              hover:bg-blue-700
              transition-all
              duration-200
            "
          >
            Choose File
          </label>

          <input
            id="file-upload"
            type="file"
            className="hidden"
            onChange={(e) =>
              setFile(
                e.target.files?.[0] || null
              )
            }
          />

          <p
            className="
              text-sm
              text-gray-600
              text-center
              break-all
            "
          >
            {
              file
                ? `Selected: ${file.name}`
                : "No file selected"
            }
          </p>

        </div>

        {/* Upload Button */}

        <button
          onClick={handleUpload}

          disabled={
            !file || loading
          }

          className={`
            w-full
            py-4
            rounded-lg
            font-semibold
            text-lg
            shadow-md
            transition-all
            duration-200

            ${
              !file || loading

                ? `
                    bg-gray-400
                    text-white
                    cursor-not-allowed
                  `

                : `
                    bg-black
                    text-white
                    hover:bg-gray-800
                  `
            }
          `}
        >

          {
            loading

              ? "Analyzing..."

              : "Upload & Analyze"
          }

        </button>

        {
  loading && (

    <div
      className="
        mt-4
        text-center
        text-blue-600
        font-medium
      "
    >

      🤖 Multi-Agent AI is analyzing the transcript...

      <br />

      ⏳ Estimated processing time:
      3–7 minutes

    </div>

  )
}

      </div>

    </main>

  );

}
