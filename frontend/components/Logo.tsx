export default function Logo() {
  return (
    <svg
      width="32"
      height="32"
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="dark:invert"
    >
      {/* Shield base */}
      <path
        d="M16 2L4 7V16C4 23.5 8.5 30.5 16 32C23.5 30.5 28 23.5 28 16V7L16 2Z"
        fill="currentColor"
      />
      {/* Checkmark */}
      <path
        d="M13 20L10 17L8 19L13 24L24 13L22 11L13 20Z"
        fill="white"
        className="dark:fill-black"
      />
    </svg>
  )
}

