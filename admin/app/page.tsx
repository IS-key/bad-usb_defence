import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import Link from "next/link"
import { Shield, List, Activity } from "lucide-react"

export default function HomePage() {
  return (
    <div className="container mx-auto py-10">
      <h1 className="text-3xl font-bold mb-8">USB Device Control System</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-green-600" />
              Управление устройствами
            </CardTitle>
            <CardDescription>Создание и управление белым списком USB-устройств</CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/devices">
              <Button className="w-full">Перейти</Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <List className="h-5 w-5 text-blue-600" />
              Журнал подключений
            </CardTitle>
            <CardDescription>Просмотр логов подключений USB-устройств</CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/logs">
              <Button className="w-full">Перейти</Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-orange-600" />
              Статус системы
            </CardTitle>
            <CardDescription>Мониторинг состояния клиентских агентов</CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/status">
              <Button className="w-full">Перейти</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
