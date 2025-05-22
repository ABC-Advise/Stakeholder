'use client';

import { Loader2 } from 'lucide-react';
import { useState } from 'react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/use-toast';

import { instagramService, PaginatedEntities } from '../services/api';

function renderResultados(info: any) {
  const output = info?.output_avaliador_seguindo_empresa;
  if (!output)
    return (
      <span className="text-zinc-400 text-sm">
        Nenhuma informação disponível ainda.
      </span>
    );

  return (
    <div className="flex flex-col gap-4">
      {/* Encontrados */}
      <div>
        <h3 className="font-bold text-green-700 mb-1">Encontrados</h3>
        {output.encontrados && output.encontrados.length > 0 ? (
          <ul className="list-disc pl-5">
            {output.encontrados.map((item: any) => (
              <li key={item.id_banco} className="mb-2">
                <span className="font-semibold">{item.full_name}</span>
                {item.username && (
                  <span className="ml-2 text-xs text-zinc-500">
                    ({item.username})
                  </span>
                )}
                <br />
                <span className="text-xs text-zinc-700">
                  {item.justificativa}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <span className="text-zinc-400 text-xs">Nenhum encontrado.</span>
        )}
      </div>
      {/* Não encontrados */}
      <div>
        <h3 className="font-bold text-red-700 mb-1">Não encontrados</h3>
        {output.nao_encontrados && output.nao_encontrados.length > 0 ? (
          <ul className="list-disc pl-5">
            {output.nao_encontrados.map((item: any) => (
              <li key={item.id_banco} className="mb-2">
                <span className="font-semibold">{item.full_name}</span>
              </li>
            ))}
          </ul>
        ) : (
          <span className="text-zinc-400 text-xs">Nenhum não encontrado.</span>
        )}
      </div>
    </div>
  );
}

export default function FluxoValidacaoPage() {
  const [cnpj, setCnpj] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [webhookInfo, setWebhookInfo] = useState<any>(null);
  const [showWebhookInfo, setShowWebhookInfo] = useState(false);
  const { toast } = useToast();

  const handleSearch = async () => {
    if (!cnpj) {
      toast({
        title: 'Erro',
        description: 'Por favor, insira um CNPJ',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);
    setShowWebhookInfo(false);
    setWebhookInfo(null);

    try {
      // Busca o CNPJ na API usando o serviço centralizado
      const data: PaginatedEntities = await instagramService.searchEntities(
        'empresa',
        cnpj
      );

      if (!data.data.length) {
        toast({
          title: 'CNPJ não encontrado',
          description: 'Nenhuma entidade encontrada para o CNPJ informado.',
          variant: 'destructive',
        });
        setWebhookInfo(null);
        return;
      }

      const entity = data.data[0];

      // Envia o ID para o webhook do n8n
      const webhookResponse = await fetch(
        'https://n8n-automacao-production.up.railway.app/webhook/dd92e331-8e22-4bf5-bd02-417f336609ee',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ entityId: entity.id }),
        }
      );
      const webhookData = await webhookResponse.json();

      setWebhookInfo(webhookData);
      setShowWebhookInfo(true);

      if (!webhookResponse.ok) {
        toast({
          title: 'Erro ao iniciar o fluxo de validação',
          description: webhookData?.message || JSON.stringify(webhookData),
          variant: 'destructive',
        });
        return;
      }

      toast({
        title: 'Sucesso',
        description: 'Fluxo de validação iniciado com sucesso!',
      });
      setCnpj(''); // Limpa o campo após sucesso
    } catch (error) {
      console.error('Erro:', error);
      setWebhookInfo({ error: 'Erro ao processar a requisição' });
      setShowWebhookInfo(true);
      toast({
        title: 'Erro',
        description: 'Erro ao processar a requisição',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-white py-12">
      <div className="w-full max-w-4xl flex flex-col md:flex-row gap-8">
        {/* Coluna 1: Validação */}
        <div className="flex-1 flex flex-col gap-8">
          <Card className="bg-white border border-zinc-200 shadow-md">
            <CardHeader>
              <CardTitle className="text-zinc-900 text-xl font-bold text-center">
                Iniciar Fluxo de Validação
              </CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <Input
                placeholder="Digite o CNPJ"
                value={cnpj}
                onChange={e => setCnpj(e.target.value)}
                className="w-full border-zinc-300"
              />
              <Button
                className="bg-black text-white font-bold w-full hover:bg-zinc-800"
                onClick={handleSearch}
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Processando...
                  </>
                ) : (
                  'Iniciar Validação'
                )}
              </Button>
            </CardContent>
          </Card>
          {/* Etapa 2 */}
          <Card className="bg-white border border-zinc-200 shadow-md">
            <CardHeader>
              <CardTitle className="text-zinc-900 text-xl font-bold text-center">
                Valida Relacionados 1<br />
                (Advogado e Sócios)
              </CardTitle>
            </CardHeader>
            <CardContent className="flex justify-center">
              <Button
                className="bg-zinc-200 text-zinc-500 font-bold w-full cursor-not-allowed"
                disabled
              >
                Em andamento
              </Button>
            </CardContent>
          </Card>
          {/* Etapa 3 (placeholder) */}
          <Card className="bg-white border border-zinc-200 shadow-md opacity-60">
            <CardHeader>
              <CardTitle className="text-zinc-900 text-xl font-bold text-center">
                Validar Empresas 2
              </CardTitle>
            </CardHeader>
            <CardContent className="flex justify-center">
              <Button
                className="bg-zinc-200 text-zinc-500 font-bold w-full cursor-not-allowed"
                disabled
              >
                Em breve
              </Button>
            </CardContent>
          </Card>
          {/* Etapa 4 (placeholder) */}
          <Card className="bg-white border border-zinc-200 shadow-md opacity-60">
            <CardHeader>
              <CardTitle className="text-zinc-900 text-xl font-bold text-center">
                Validar Sócios 2
              </CardTitle>
            </CardHeader>
            <CardContent className="flex justify-center">
              <Button
                className="bg-zinc-200 text-zinc-500 font-bold w-full cursor-not-allowed"
                disabled
              >
                Em breve
              </Button>
            </CardContent>
          </Card>
        </div>
        {/* Coluna 2: Informações do processo */}
        {showWebhookInfo && (
          <div className="flex-1">
            <Card className="bg-white border border-zinc-200 shadow-md h-full max-h-[500px] flex flex-col">
              <CardHeader>
                <CardTitle className="text-zinc-900 text-xl font-bold text-center">
                  Informações do processo
                </CardTitle>
              </CardHeader>
              <CardContent className="overflow-y-auto flex-1">
                {isLoading ? (
                  <div className="flex flex-col items-center justify-center gap-2 py-4">
                    <Loader2 className="h-8 w-8 animate-spin text-zinc-400" />
                    <span className="text-zinc-500 text-sm">
                      Aguardando resposta do processo...
                    </span>
                  </div>
                ) : webhookInfo ? (
                  renderResultados(webhookInfo)
                ) : (
                  <span className="text-zinc-400 text-sm">
                    Nenhuma informação disponível ainda.
                  </span>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
