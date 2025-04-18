"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { toast } from "@/components/ui/use-toast"
import { RefreshCw } from "lucide-react"

interface ClientStatus {
  id: number
  computer_name: string
  ip_address: string
  user: string
  os: string
  last_seen: string
  status: "online" | "offline"
  version: string
}

export default function StatusPage() {
  const [clients, setClients] = useState<ClientStatus[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchClientStatus()
    // Set up polling every 30 seconds
    const interval = setInterval(fetchClientStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchClientStatus = async () => {
    try {
      setLoading(true)
      const response = await fetch("http://localhost:5000/api/clients")
      if (response.ok) {
        const data = await response.json()
        setClients(data)
      } else {
        toast({
          title: "Ошибка",
          description: "Не удалось загрузить статус клиентских агентов",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Error fetching client status:", error)
      toast({
        title: "Ошибка соединения",
        description: "Не удалось подключиться к серверу",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto py-10">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Статус клиентских агентов</CardTitle>
          <Button variant="outline" onClick={fetchClientStatus}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Обновить
          </Button>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-10">
              <p>Загрузка...</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Компьютер</TableHead>
                  <TableHead>IP-адрес</TableHead>
                  <TableHead>Пользователь</TableHead>
                  <TableHead>ОС</TableHead>
                  <TableHead>Последняя активность</TableHead>
                  <TableHead>Статус</TableHead>
                  <TableHead>Версия агента</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {clients.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-10">
                      Нет подключенных клиентских агентов
                    </TableCell>
                  </TableRow>
                ) : (
                  clients.map((client) => (
                    <TableRow key={client.id}>
                      <TableCell>{client.computer_name}</TableCell>
                      <TableCell>{client.ip_address}</TableCell>
                      <TableCell>{client.user}</TableCell>
                      <TableCell>{client.os}</TableCell>
                      <TableCell>{new Date(client.last_seen).toLocaleString()}</TableCell>
                      <TableCell>
                        <Badge
                          variant={client.status === "online" ? "success" : "secondary"}
                          className={
                            client.status === "online" ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"
                          }
                        >
                          {client.status === "online" ? "Онлайн" : "Офлайн"}
                        </Badge>
                      </TableCell>
                      <TableCell>{client.version}</TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
