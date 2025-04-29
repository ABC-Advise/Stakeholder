import { Log as LogType } from '@/http/logs/get-logs-by-id'
import { cn } from '@/lib/utils'

type LogProps = {
  data: LogType
}

export function Log({ data }: LogProps) {
  return (
    <div
      className={cn(
        'flex min-h-8 w-full items-center gap-2 p-2 hover:bg-muted',
        data.tipo_log_nome === 'ERROR' && 'bg-rose-100 text-rose-500',
        data.tipo_log_nome === 'WARN' && 'bg-amber-100 text-amber-500',
      )}
    >
      <p className="text-sm">
        {data.data_log} - {data.tipo_log_nome} {data.mensagem}
      </p>
    </div>
  )
}
