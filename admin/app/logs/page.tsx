"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Search, Download, RefreshCw } from "lucide-react"
import { toast } from "@/components/ui/use-toast"
import { Badge } from "@/components/ui/badge"

interface LogEntry {
  id: number
  timestamp: string
  device_name: string
  vid: string
  pid: string
  serial_number: string
  status: "allowed" | "blocked"
  computer_name: string
  ip_address: string
  user: string
}

export default function LogsPage() {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("all")

  useEffect(() => {
    fetchLogs()
  }, [])

  const fetchLogs = async () => {
    try {
      setLoading(true)
      const response = await fetch("http://localhost:5000/api/logs")
      if (response.ok) {
        const data = await response.json()
        setLogs(data)
      } else {
        toast({
          title: "Ошибка",
          description: "Не удалось загрузить журнал подключений",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Error fetching logs:", error)
      toast({
        title: "Ошибка соединения",
        description: "Не удалось подключиться к серверу",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleExportLogs = () => {
    try {
      // Create CSV content
      const headers = [
        "ID",
        "Время",
        "Устройство",
        "VID",
        "PID",
        "Серийный номер",
        "Статус",
        "Компьютер",
        "IP-адрес",
        "Пользователь",
      ]

      const csvContent = [
        headers.join(","),
        ...filteredLogs.map((log) =>
          [
            log.id,
            log.timestamp,
            log.device_name,
            log.vid,
            log.pid,
            log.serial_number,
            log.status === "allowed" ? "Разрешено" : "Заблокировано",
            log.computer_name,
            log.ip_address,
            log.user,
          ].join(","),
        ),
      ].join("\n")

      // Create and download the file
      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
      const url = URL.createObjectURL(blob)
      const link = document.createElement("a")
      link.setAttribute("href", url)
      link.setAttribute("download", `usb_logs_${new Date().toISOString().split("T")[0]}.csv`)
      link.style.visibility = "hidden"
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      toast({
        title: "Экспорт выполнен",
        description: "Журнал подключений успешно экспортирован в CSV",
      })
    } catch (error) {
      console.error("Error exporting logs:", error)
      toast({
        title: "Ошибка экспорта",
        description: "Не удалось экспортировать журнал подключений",
        variant: "destructive",
      })
    }
  }

  const filteredLogs = logs.filter((log) => {
    const matchesSearch =
      log.device_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.vid.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.pid.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.serial_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.computer_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.ip_address.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.user.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesStatus =
      statusFilter === "all" ||
      (statusFilter === "allowed" && log.status === "allowed") ||
      (statusFilter === "blocked" && log.status === "blocked")

    return matchesSearch && matchesStatus
  })

  return (
    <div className="container mx-auto py-10">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Журнал подключений USB-устройств</CardTitle>
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                type="search"
                placeholder="Поиск..."
                className="w-[250px] pl-8"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Статус" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Все статусы</SelectItem>
                <SelectItem value="allowed">Разрешено</SelectItem>
                <SelectItem value="blocked">Заблокировано</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" onClick={fetchLogs}>
              <RefreshCw className="mr-2 h-4 w-4" />
              Обновить
            </Button>
            <Button onClick={handleExportLogs}>
              <Download className="mr-2 h-4 w-4" />
              Экспорт CSV
            </Button>
          </div>
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
                  <TableHead>Время</TableHead>
                  <TableHead>Устройство</TableHead>
                  <TableHead>VID:PID</TableHead>
                  <TableHead>Серийный номер</TableHead>
                  <TableHead>Статус</TableHead>
                  <TableHead>Компьютер</TableHead>
                  <TableHead>IP-адрес</TableHead>
                  <TableHead>Пользователь</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredLogs.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-10">
                      {searchTerm || statusFilter !== "all" ? "Записи не найдены" : "Журнал подключений пуст"}
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredLogs.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell>{new Date(log.timestamp).toLocaleString()}</TableCell>
                      <TableCell>{log.device_name}</TableCell>
                      <TableCell>{`${log.vid}:${log.pid}`}</TableCell>
                      <TableCell>{log.serial_number}</TableCell>
                      <TableCell>
                        <Badge variant={log.status === "allowed" ? "outline" : "destructive"}>
                          {log.status === "allowed" ? "Разрешено" : "Заблокировано"}
                        </Badge>
                      </TableCell>
                      <TableCell>{log.computer_name}</TableCell>
                      <TableCell>{log.ip_address}</TableCell>
                      <TableCell>{log.user}</TableCell>
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
