import { useState } from 'react'
import { Gear, Image } from '@phosphor-icons/react'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { useKV } from '@github/spark/hooks'
import { toast } from 'sonner'

export function SettingsModal() {
  const [logoUrl, setLogoUrl] = useKV('logo-url', '')
  const [logoText, setLogoText] = useKV('logo-text', 'DTM Task Manager')
  const [showLogo, setShowLogoKV] = useKV('show-logo', 'true')
  const [open, setOpen] = useState(false)

  const setShowLogoValue = (checked: boolean) => {
    setShowLogoKV(checked ? 'true' : 'false')
  }

  const showLogoBoolean = showLogo === 'true'

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const result = e.target?.result as string
        setLogoUrl(result)
        toast.success('Logo uploaded successfully')
      }
      reader.readAsDataURL(file)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Gear className="h-4 w-4 mr-2" />
          Settings
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Settings</DialogTitle>
          <DialogDescription>
            Customize your DTM Task Manager branding and preferences.
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-6">
          {/* Logo Settings */}
          <div className="space-y-4">
            <Label className="text-base font-medium flex items-center gap-2">
              <Image className="h-4 w-4" />
              Logo & Branding
            </Label>
            
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Switch
                  id="show-logo"
                  checked={showLogoBoolean}
                  onCheckedChange={setShowLogoValue}
                />
                <Label htmlFor="show-logo">Show logo in header</Label>
              </div>

              {showLogoBoolean && (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="logo-text">Logo Text</Label>
                    <Input
                      id="logo-text"
                      value={logoText || ''}
                      onChange={(e) => setLogoText(e.target.value)}
                      placeholder="Enter logo text"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="logo-upload">Custom Logo Image</Label>
                    <div className="flex gap-2">
                      <Input
                        id="logo-upload"
                        type="file"
                        accept="image/*"
                        onChange={handleFileUpload}
                        className="file:mr-2 file:py-1 file:px-2 file:border-0 file:bg-muted file:text-foreground"
                      />
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => setLogoUrl('')}
                      >
                        Clear
                      </Button>
                    </div>
                    {logoUrl && (
                      <div className="mt-2">
                        <img
                          src={logoUrl}
                          alt="Logo preview"
                          className="h-12 w-auto rounded border"
                        />
                      </div>
                    )}
                  </div>

                  <div className="p-3 bg-muted rounded-lg">
                    <div className="text-sm text-muted-foreground mb-2">Preview:</div>
                    <div className="flex items-center gap-3">
                      {logoUrl ? (
                        <img src={logoUrl} alt="Logo" className="h-8 w-auto" />
                      ) : (
                        <div className="h-8 w-8 rounded bg-primary/10 flex items-center justify-center">
                          <Image className="h-4 w-4 text-primary" />
                        </div>
                      )}
                      <span className="font-semibold">{logoText || 'DTM Task Manager'}</span>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-2 pt-4 border-t">
          <Button variant="outline" onClick={() => setOpen(false)}>
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}