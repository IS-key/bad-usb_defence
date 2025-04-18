"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Plus, Pencil, Trash2, Search } from "lucide-react"
import { toast } from "@/components/ui/use-toast"

interface Device {
  id: number
  name: string
  vid: string
  pid: string
  serial_number: string
  description: string
  added_date: string
}

export default function DevicesPage() {
  const [devices, setDevices] = useState<Device[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [currentDevice, setCurrentDevice] = useState<Device | null>(null)
  const [formData, setFormData] = useState({
    name: "",
    vid: "",
    pid: "",
    serial_number: "",
    description: "",
  })

  useEffect(() => {
    fetchDevices()
  }, [])

  const fetchDevices = async () => {
    try {
      setLoading(true)
      const response = await fetch("http://localhost:5000/api/devices")
      if (response.ok) {
        const data = await response.json()
        setDevices(data)
      } else {
        toast({
          title: "Ошибка",
          description: "Не удалось загрузить список устройств",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Error fetching devices:", error)
      toast({
        title: "Ошибка соединения",
        description: "Не удалось подключиться к серверу",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleAddDevice = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/devices", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        toast({
          title: "Устройство добавлено",
          description: "Устройство успешно добавлено в белый список",
        })
        fetchDevices()
        setIsAddDialogOpen(false)
        resetForm()
      } else {
        const error = await response.json()
        toast({
          title: "Ошибка",
          description: error.message || "Не удалось добавить устройство",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Error adding device:", error)
      toast({
        title: "Ошибка соединения",
        description: "Не удалось подключиться к серверу",
        variant: "destructive",
      })
    }
  }

  const handleEditDevice = async () => {
    if (!currentDevice) return

    try {
      const response = await fetch(`http://localhost:5000/api/devices/${currentDevice.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        toast({
          title: "Устройство обновлено",
          description: "Информация об устройстве успешно обновлена",
        })
        fetchDevices()
        setIsEditDialogOpen(false)
        resetForm()
      } else {
        const error = await response.json()
        toast({
          title: "Ошибка",
          description: error.message || "Не удалось обновить устройство",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Error updating device:", error)
      toast({
        title: "Ошибка соединения",
        description: "Не удалось подключиться к серверу",
        variant: "destructive",
      })
    }
  }

  const handleDeleteDevice = async (id: number) => {
    if (!confirm("Вы уверены, что хотите удалить это устройство?")) return

    try {
      const response = await fetch(`http://localhost:5000/api/devices/${id}`, {
        method: "DELETE",
      })

      if (response.ok) {
        toast({
          title: "Устройство удалено",
          description: "Устройство успешно удалено из белого списка",
        })
        fetchDevices()
      } else {
        const error = await response.json()
        toast({
          title: "Ошибка",
          description: error.message || "Не удалось удалить устройство",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Error deleting device:", error)
      toast({
        title: "Ошибка соединения",
        description: "Не удалось подключиться к серверу",
        variant: "destructive",
      })
    }
  }

  const openEditDialog = (device: Device) => {
    setCurrentDevice(device)
    setFormData({
      name: device.name,
      vid: device.vid,
      pid: device.pid,
      serial_number: device.serial_number,
      description: device.description,
    })
    setIsEditDialogOpen(true)
  }

  const resetForm = () => {
    setFormData({
      name: "",
      vid: "",
      pid: "",
      serial_number: "",
      description: "",
    })
    setCurrentDevice(null)
  }

  const filteredDevices = devices.filter(
    (device) =>
      device.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      device.vid.toLowerCase().includes(searchTerm.toLowerCase()) ||
      device.pid.toLowerCase().includes(searchTerm.toLowerCase()) ||
      device.serial_number.toLowerCase().includes(searchTerm.toLowerCase()),
  )

  return (
    <div className="container mx-auto py-10">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Белый список USB-устройств</CardTitle>
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
            <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
              <DialogTrigger asChild>
                <Button onClick={() => resetForm()}>
                  <Plus className="mr-2 h-4 w-4" />
                  Добавить устройство
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Добавить новое устройство</DialogTitle>
                  <DialogDescription>
                    Заполните информацию о USB-устройстве для добавления в белый список
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="name" className="text-right">
                      Название
                    </Label>
                    <Input
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      className="col-span-3"
                    />
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="vid" className="text-right">
                      VID
                    </Label>
                    <Input
                      id="vid"
                      name="vid"
                      value={formData.vid}
                      onChange={handleInputChange}
                      className="col-span-3"
                      placeholder="Например: 0x1234"
                    />
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="pid" className="text-right">
                      PID
                    </Label>
                    <Input
                      id="pid"
                      name="pid"
                      value={formData.pid}
                      onChange={handleInputChange}
                      className="col-span-3"
                      placeholder="Например: 0x5678"
                    />
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="serial_number" className="text-right">
                      Серийный номер
                    </Label>
                    <Input
                      id="serial_number"
                      name="serial_number"
                      value={formData.serial_number}
                      onChange={handleInputChange}
                      className="col-span-3"
                    />
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="description" className="text-right">
                      Описание
                    </Label>
                    <Input
                      id="description"
                      name="description"
                      value={formData.description}
                      onChange={handleInputChange}
                      className="col-span-3"
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                    Отмена
                  </Button>
                  <Button onClick={handleAddDevice}>Добавить</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
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
                  <TableHead>Название</TableHead>
                  <TableHead>VID</TableHead>
                  <TableHead>PID</TableHead>
                  <TableHead>Серийный номер</TableHead>
                  <TableHead>Описание</TableHead>
                  <TableHead>Дата добавления</TableHead>
                  <TableHead className="text-right">Действия</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredDevices.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-10">
                      {searchTerm ? "Устройства не найдены" : "Белый список пуст. Добавьте устройства."}
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredDevices.map((device) => (
                    <TableRow key={device.id}>
                      <TableCell>{device.name}</TableCell>
                      <TableCell>{device.vid}</TableCell>
                      <TableCell>{device.pid}</TableCell>
                      <TableCell>{device.serial_number}</TableCell>
                      <TableCell>{device.description}</TableCell>
                      <TableCell>{new Date(device.added_date).toLocaleDateString()}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button variant="outline" size="icon" onClick={() => openEditDialog(device)}>
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button variant="outline" size="icon" onClick={() => handleDeleteDevice(device.id)}>
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Редактировать устройство</DialogTitle>
            <DialogDescription>Измените информацию об USB-устройстве</DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit-name" className="text-right">
                Название
              </Label>
              <Input
                id="edit-name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit-vid" className="text-right">
                VID
              </Label>
              <Input
                id="edit-vid"
                name="vid"
                value={formData.vid}
                onChange={handleInputChange}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit-pid" className="text-right">
                PID
              </Label>
              <Input
                id="edit-pid"
                name="pid"
                value={formData.pid}
                onChange={handleInputChange}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit-serial" className="text-right">
                Серийный номер
              </Label>
              <Input
                id="edit-serial"
                name="serial_number"
                value={formData.serial_number}
                onChange={handleInputChange}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit-description" className="text-right">
                Описание
              </Label>
              <Input
                id="edit-description"
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                className="col-span-3"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Отмена
            </Button>
            <Button onClick={handleEditDevice}>Сохранить</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
