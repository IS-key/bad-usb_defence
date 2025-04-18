import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Shield } from "lucide-react"

export default function Navbar() {
  return (
    <header className="border-b">
      <div className="container mx-auto flex h-16 items-center justify-between">
        <div className="flex items-center gap-2">
          <Shield className="h-6 w-6 text-green-600" />
          <Link href="/" className="text-xl font-bold">
            USB Control
          </Link>
        </div>
        <nav className="flex items-center gap-6">
          <Link href="/devices" className="text-sm font-medium hover:underline">
            Устройства
          </Link>
          <Link href="/logs" className="text-sm font-medium hover:underline">
            Журнал
          </Link>
          <Link href="/status" className="text-sm font-medium hover:underline">
            Статус
          </Link>
          <Button variant="outline" size="sm">
            Выход
          </Button>
        </nav>
      </div>
    </header>
  )
}
