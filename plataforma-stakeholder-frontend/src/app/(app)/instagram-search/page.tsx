'use client';

import {
  Search,
  RefreshCw,
  Loader2,
  UserSearch,
  Play,
  List,
  Users,
  Building,
  Briefcase,
} from 'lucide-react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { useState, useEffect, useCallback } from 'react';

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/components/ui/use-toast';

import { EntitiesTable } from './components/entities-table';
import {
  instagramService,
  type DashboardData,
  type Entidade,
  type UltimaBusca,
  type PaginatedEntities,
  type ResultadoBusca,
} from './services/api';

interface BulkResultState {
  empresas: ResultadoBusca[];
  pessoas: ResultadoBusca[];
  advogados: ResultadoBusca[];
}

const API_URL = process.env.NEXT_PUBLIC_INSTAGRAM_API_URL;

export default function InstagramSearchPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [loadingDashboard, setLoadingDashboard] = useState(false);
  const [dashboardCarregado, setDashboardCarregado] = useState(false);
  const [loadingBuscaTodos, setLoadingBuscaTodos] = useState(false);
  const [dashboardData, setDashboardData] = useState<DashboardData>({
    estatisticas: [],
    ultimas_buscas: [],
  });
  const [entidades, setEntidades] = useState<Entidade[]>([]);
  const [loadingEntidades, setLoadingEntidades] = useState(false);
  const [entidadesCarregadas, setEntidadesCarregadas] = useState(false);

  // Estados para busca por identificador
  const [identifierSearchType, setIdentifierSearchType] = useState<
    'empresa' | 'pessoa' | 'advogado' | ''
  >('');
  const [identifierSearchValue, setIdentifierSearchValue] = useState('');
  const [loadingIdentifierSearch, setLoadingIdentifierSearch] = useState(false);

  // Estado para armazenar resultados da busca em massa
  const [bulkResults, setBulkResults] = useState<BulkResultState | null>(null);
  const [loadingBulkResults, setLoadingBulkResults] = useState(false);

  // --- NOVOS ESTADOS PARA BUSCA DE RELACIONADOS ---
  const [cnpjEmpresa, setCnpjEmpresa] = useState('');
  const [loadingRelated, setLoadingRelated] = useState(false);
  const [relatedResult, setRelatedResult] = useState<any>(null);

  // --- NOVOS ESTADOS PARA TABELAS SEPARADAS E PAGINAÇÃO COMPLETA ---
  const [empresas, setEmpresas] = useState<Entidade[]>([]);
  const [pessoas, setPessoas] = useState<Entidade[]>([]);
  const [advogados, setAdvogados] = useState<Entidade[]>([]);
  const [buscaEmpresa, setBuscaEmpresa] = useState('');
  const [buscaPessoa, setBuscaPessoa] = useState('');
  const [buscaAdvogado, setBuscaAdvogado] = useState('');
  const [paginaEmpresa, setPaginaEmpresa] = useState(1);
  const [paginaPessoa, setPaginaPessoa] = useState(1);
  const [paginaAdvogado, setPaginaAdvogado] = useState(1);
  const [limiteEmpresa, setLimiteEmpresa] = useState(10);
  const [limitePessoa, setLimitePessoa] = useState(10);
  const [limiteAdvogado, setLimiteAdvogado] = useState(10);
  const [totalEmpresas, setTotalEmpresas] = useState(0);
  const [totalPessoas, setTotalPessoas] = useState(0);
  const [totalAdvogados, setTotalAdvogados] = useState(0);
  const [inputPaginaEmpresa, setInputPaginaEmpresa] = useState('1');
  const [inputPaginaPessoa, setInputPaginaPessoa] = useState('1');
  const [inputPaginaAdvogado, setInputPaginaAdvogado] = useState('1');

  // --- ESTADOS PARA BUSCA AVANÇADA DE ENTIDADES ---
  const [tipoBusca, setTipoBusca] = useState<'empresa' | 'pessoa' | 'advogado'>(
    'empresa'
  );
  const [termoBusca, setTermoBusca] = useState('');
  const [resultadosBusca, setResultadosBusca] = useState<Entidade[]>([]);
  const [paginaBusca, setPaginaBusca] = useState(1);
  const [limiteBusca, setLimiteBusca] = useState(10);
  const [totalBusca, setTotalBusca] = useState(0);
  const [inputPaginaBusca, setInputPaginaBusca] = useState('1');
  const [loadingBuscaAvancada, setLoadingBuscaAvancada] = useState(false);

  // Estado para edição manual de Instagram na busca geral
  const [editandoInstagram, setEditandoInstagram] = useState<{
    tipo: string;
    index: number;
  } | null>(null);
  const [valorInstagramManual, setValorInstagramManual] = useState<string>('');

  const numPaginasBusca = Math.ceil(totalBusca / limiteBusca) || 1;

  // Estado para mensagens de erro
  const [mensagemErro, setMensagemErro] = useState<string | null>(null);

  // Função para carregar dados do dashboard (stats e últimas buscas)
  const carregarDashboardData = useCallback(async () => {
    setLoadingDashboard(true);
    setDashboardCarregado(true);
    try {
      const data = await instagramService.getDashboardData();
      setDashboardData(data);
    } catch (error) {
      console.error('Erro ao carregar dados do dashboard:', error);
      toast({
        title: 'Erro no Dashboard',
        description:
          'Não foi possível carregar as estatísticas e últimas buscas.',
        variant: 'destructive',
      });
      setDashboardCarregado(false);
    } finally {
      setLoadingDashboard(false);
    }
  }, [toast]);

  // Função para carregar entidades paginadas por tipo
  const carregarEntidadesTipo = useCallback(
    async (
      tipo: 'empresa' | 'pessoa' | 'advogado',
      pagina: number,
      limite: number
    ) => {
      setLoadingEntidades(true);
      try {
        const response = await instagramService.getEntitiesByTypePaginated(
          tipo,
          pagina,
          limite
        );
        if (tipo === 'empresa') {
          setEmpresas(response.data);
          setTotalEmpresas(response.total);
        } else if (tipo === 'pessoa') {
          setPessoas(response.data);
          setTotalPessoas(response.total);
        } else if (tipo === 'advogado') {
          setAdvogados(response.data);
          setTotalAdvogados(response.total);
        }
      } catch (error) {
        toast({
          title: 'Erro ao listar entidades',
          description: 'Não foi possível carregar a lista.',
          variant: 'destructive',
        });
      } finally {
        setLoadingEntidades(false);
      }
    },
    [toast]
  );

  // Carregar entidades ao clicar no botão
  const carregarEntidades = useCallback(async () => {
    setEntidadesCarregadas(true);
    setPaginaEmpresa(1);
    setPaginaPessoa(1);
    setPaginaAdvogado(1);
    setInputPaginaEmpresa('1');
    setInputPaginaPessoa('1');
    setInputPaginaAdvogado('1');
    await Promise.all([
      carregarEntidadesTipo('empresa', 1, limiteEmpresa),
      carregarEntidadesTipo('pessoa', 1, limitePessoa),
      carregarEntidadesTipo('advogado', 1, limiteAdvogado),
    ]);
  }, [carregarEntidadesTipo, limiteEmpresa, limitePessoa, limiteAdvogado]);

  // Atualizar ao mudar de página ou limite
  useEffect(() => {
    if (entidadesCarregadas) {
      carregarEntidadesTipo('empresa', paginaEmpresa, limiteEmpresa);
    }
  }, [
    paginaEmpresa,
    limiteEmpresa,
    carregarEntidadesTipo,
    entidadesCarregadas,
  ]);

  useEffect(() => {
    if (entidadesCarregadas) {
      carregarEntidadesTipo('pessoa', paginaPessoa, limitePessoa);
    }
  }, [paginaPessoa, limitePessoa, carregarEntidadesTipo, entidadesCarregadas]);

  useEffect(() => {
    if (entidadesCarregadas) {
      carregarEntidadesTipo('advogado', paginaAdvogado, limiteAdvogado);
    }
  }, [
    paginaAdvogado,
    limiteAdvogado,
    carregarEntidadesTipo,
    entidadesCarregadas,
  ]);

  // Calcular número de páginas
  const numPaginasEmpresas = Math.ceil(totalEmpresas / limiteEmpresa) || 1;
  const numPaginasPessoas = Math.ceil(totalPessoas / limitePessoa) || 1;
  const numPaginasAdvogados = Math.ceil(totalAdvogados / limiteAdvogado) || 1;

  // Handler para o botão "Buscar Todos"
  const handleBuscarTodos = async () => {
    setLoadingBuscaTodos(true);
    setBulkResults(null); // Limpa resultados anteriores
    setLoadingBulkResults(true);
    const tipos: ('empresa' | 'pessoa' | 'advogado')[] = [
      'empresa',
      'pessoa',
      'advogado',
    ];
    let hasError = false;

    try {
      for (const tipo of tipos) {
        toast({ title: `Iniciando busca em massa para ${tipo}s...` });
        try {
          const apiResponse =
            await instagramService.findAllInstagramForEntityType(tipo);
          const tipoResult = apiResponse.results || [];
          setBulkResults(prev => ({
            empresas:
              tipo === 'empresa' ? tipoResult : prev ? prev.empresas : [],
            pessoas: tipo === 'pessoa' ? tipoResult : prev ? prev.pessoas : [],
            advogados:
              tipo === 'advogado' ? tipoResult : prev ? prev.advogados : [],
          }));
          toast({
            title: `Busca para ${tipo}s concluída`,
            description: `${tipoResult.length} entidades processadas.`,
          });
        } catch (error: any) {
          console.error(`Erro na busca em massa para ${tipo}:`, error);
          const erroArray = [
            {
              error: `Falha ao buscar ${tipo}s: ${error.message || 'Erro desconhecido'}`,
              entity: {} as Entidade,
              candidates: [],
              validated_profile: null,
            },
          ];
          setBulkResults(prev => ({
            empresas:
              tipo === 'empresa' ? erroArray : prev ? prev.empresas : [],
            pessoas: tipo === 'pessoa' ? erroArray : prev ? prev.pessoas : [],
            advogados:
              tipo === 'advogado' ? erroArray : prev ? prev.advogados : [],
          }));
          toast({
            title: `Erro na busca para ${tipo}s`,
            description: error.message || 'Erro desconhecido',
            variant: 'destructive',
          });
          hasError = true;
        }
      }
      if (!hasError) {
        toast({
          title: 'Busca em Massa Concluída',
          description: 'Todas as buscas foram processadas.',
        });
      }
    } catch (error) {
      // Este catch é mais para erros inesperados no loop
      console.error('Erro inesperado durante a busca em massa:', error);
      toast({
        title: 'Erro Geral na Busca',
        description:
          'Ocorreu um erro inesperado ao processar as buscas em massa.',
        variant: 'destructive',
      });
    } finally {
      setLoadingBuscaTodos(false);
      setLoadingBulkResults(false);
    }
  };

  // Handler para o botão "Buscar" individual na tabela
  const handleSearchIndividual = async (entidade: Entidade) => {
    if (!entidade.tipo) {
      toast({
        title: 'Erro de Dados',
        description:
          'Não é possível buscar detalhes para esta entidade pois faltam informações (Tipo).',
        variant: 'destructive',
      });
      return;
    }

    let tipoEntidade = (entidade.tipo || '').trim();
    let identifier = '';
    if (tipoEntidade === 'empresa') identifier = (entidade.cnpj || '').trim();
    else if (tipoEntidade === 'pessoa')
      identifier = (entidade.cpf || '').trim();
    else if (tipoEntidade === 'advogado')
      identifier = (entidade.cpf || entidade.oab || '').trim();

    if (!identifier) {
      toast({
        title: 'Erro de Dados',
        description:
          'Não foi possível encontrar o identificador correto (CNPJ, CPF ou OAB) para esta entidade.',
        variant: 'destructive',
      });
      return;
    }

    toast({
      title: 'Iniciando Busca',
      description: `Iniciando busca para ${entidade.nome}...`,
    });
    try {
      // Se quiser chamar a API para iniciar a busca, descomente a linha abaixo:
      // await instagramService.findInstagramForEntity(tipoEntidade, identifier);
      // Redireciona para a busca individual usando o identifier correto
      router.push(`/instagram-search/${tipoEntidade}/${identifier}`);
    } catch (error) {
      toast({
        title: 'Erro na Busca',
        description: `Não foi possível iniciar a busca para ${entidade.nome}.`,
        variant: 'destructive',
      });
    }
  };

  // Handler para busca por identificador
  const handleIdentifierSearch = async () => {
    const tipo = (identifierSearchType || '').toString().trim().toLowerCase();
    const identifier = (identifierSearchValue || '').toString().trim();

    if (!tipo || !identifier) {
      setMensagemErro('Por favor, selecione o tipo e informe o identificador.');
      return;
    }

    if (!['empresa', 'pessoa', 'advogado'].includes(tipo)) {
      setMensagemErro('Tipo de entidade inválido.');
      return;
    }

    router.push(`/instagram-search/${tipo}/${identifier}`);
  };

  // Handlers para buscas em massa específicas
  const handleBuscarPendentesTipo = async (
    tipo: 'empresa' | 'pessoa' | 'advogado'
  ) => {
    setLoadingBuscaTodos(true);
    setBulkResults(null);
    setLoadingBulkResults(true);
    try {
      toast({ title: `Iniciando busca em massa para ${tipo}s...` });
      const apiResponse =
        await instagramService.findAllInstagramForEntityType(tipo);
      const tipoResult = apiResponse.results || [];
      setBulkResults(prev => ({
        empresas:
          tipo === 'empresa'
            ? tipoResult
            : prev && prev.empresas
              ? prev.empresas
              : [],
        pessoas:
          tipo === 'pessoa'
            ? tipoResult
            : prev && prev.pessoas
              ? prev.pessoas
              : [],
        advogados:
          tipo === 'advogado'
            ? tipoResult
            : prev && prev.advogados
              ? prev.advogados
              : [],
      }));
      toast({
        title: `Busca para ${tipo}s concluída`,
        description: `${tipoResult.length} entidades processadas.`,
      });
    } catch (error: any) {
      console.error(`Erro na busca em massa para ${tipo}: `, error);
      const erroArray = [
        {
          error: `Falha ao buscar ${tipo}s: ${error.message || 'Erro desconhecido'}`,
          entity: {} as Entidade,
          candidates: [],
          validated_profile: null,
        },
      ];
      setBulkResults(prev => ({
        empresas:
          tipo === 'empresa'
            ? erroArray
            : prev && prev.empresas
              ? prev.empresas
              : [],
        pessoas:
          tipo === 'pessoa'
            ? erroArray
            : prev && prev.pessoas
              ? prev.pessoas
              : [],
        advogados:
          tipo === 'advogado'
            ? erroArray
            : prev && prev.advogados
              ? prev.advogados
              : [],
      }));
      toast({
        title: `Erro na busca para ${tipo}s`,
        description: error.message || 'Erro desconhecido',
        variant: 'destructive',
      });
    } finally {
      setLoadingBuscaTodos(false);
      setLoadingBulkResults(false);
    }
  };

  const handleBuscaAvancada = async (pagina = 1, limite = limiteBusca) => {
    if (!termoBusca.trim()) {
      toast({
        title: 'Campo obrigatório',
        description: 'Digite um termo para buscar.',
        variant: 'destructive',
      });
      return;
    }
    setLoadingBuscaAvancada(true);
    try {
      const response = await instagramService.searchEntities(
        tipoBusca,
        termoBusca.trim(),
        pagina,
        limite
      );
      setResultadosBusca(response.data);
      setTotalBusca(response.total);
      setPaginaBusca(pagina);
      setInputPaginaBusca(String(pagina));
    } catch (error) {
      toast({
        title: 'Erro na busca',
        description: 'Não foi possível buscar entidades.',
        variant: 'destructive',
      });
    } finally {
      setLoadingBuscaAvancada(false);
    }
  };

  // Função para confirmar Instagram manualmente
  const handleConfirmarInstagramManual = async (
    tipo: string,
    res: any,
    index: number
  ) => {
    if (!valorInstagramManual.trim()) {
      toast({
        title: 'Campo obrigatório',
        description: 'Informe o @instagram.',
        variant: 'destructive',
      });
      return;
    }
    try {
      await instagramService.confirmInstagramProfile(
        res.entity.tipo,
        res.entity.id,
        valorInstagramManual.trim()
      );
      toast({
        title: 'Instagram confirmado!',
        description: `O perfil @${valorInstagramManual.trim()} foi salvo.`,
      });
      // Atualiza a lista após confirmação
      setBulkResults(prev => {
        if (!prev) return prev;
        const novo = { ...prev };
        const tipoKey = tipo as keyof BulkResultState;
        const arr = [...novo[tipoKey]];
        arr[index] = {
          ...arr[index],
          validated_profile: {
            perfil: {
              username: valorInstagramManual.trim(),
              profile_pic_url: '',
              full_name: '',
              pk: 0,
              is_private: false,
              is_verified: false,
              bio: '',
              is_business: false,
            },
            score: 100,
            is_business_profile: false,
          },
        };
        novo[tipoKey] = arr;
        return novo;
      });
      setEditandoInstagram(null);
      setValorInstagramManual('');
    } catch (error: any) {
      toast({
        title: 'Erro ao confirmar',
        description: error.message || 'Erro desconhecido',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="container mx-auto py-6">
      {mensagemErro && (
        <div
          style={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            minWidth: 280,
            maxWidth: 360,
            zIndex: 9999,
            background: '#fee2e2',
            color: '#b91c1c',
            padding: '16px 24px 16px 16px',
            borderRadius: 8,
            boxShadow: '0 2px 12px rgba(0,0,0,0.12)',
            fontWeight: 'bold',
            display: 'flex',
            alignItems: 'center',
            gap: 8,
          }}
        >
          <span style={{ flex: 1 }}>{mensagemErro}</span>
          <button
            style={{
              color: '#b91c1c',
              background: 'none',
              border: 'none',
              fontWeight: 'bold',
              fontSize: 18,
              cursor: 'pointer',
              marginLeft: 8,
            }}
            onClick={() => setMensagemErro(null)}
            aria-label="Fechar"
          >
            ×
          </button>
        </div>
      )}
      <h1 className="text-3xl font-bold mb-6">Instagram Profile Finder</h1>

      {/* Últimas Buscas do Dashboard */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Últimas Buscas</CardTitle>
        </CardHeader>
        <CardContent>
          {loadingDashboard ? (
            <div>Carregando buscas...</div>
          ) : dashboardData.ultimas_buscas ? (
            <div className="space-y-2">
              {dashboardData.ultimas_buscas.map(b => (
                <div
                  key={b.nome + b.data}
                  className="flex flex-col md:flex-row md:items-center md:gap-4 p-2 border rounded bg-white"
                >
                  <span className="font-medium">
                    {b.nome}{' '}
                    <span className="text-xs text-gray-500">({b.tipo})</span>
                  </span>
                  <span
                    className={`text - xs font - semibold ${b.status === 'concluida' ? 'text-green-600' : b.status === 'em_andamento' ? 'text-blue-600' : 'text-red-600'}`}
                  >
                    Status: {b.status}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(b.data).toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div>Nenhuma busca recente encontrada.</div>
          )}
        </CardContent>
      </Card>

      {/* Cards de Estatísticas */}
      <h2 className="text-xl font-semibold mb-3">Estatísticas</h2>
      {loadingDashboard ? (
        <div className="flex gap-2 mb-6">
          {[...Array(3)].map((_, i) => (
            <div
              key={i}
              className="h-12 w-32 bg-gray-200 rounded animate-pulse"
            ></div>
          ))}
        </div>
      ) : (
        <div className="flex gap-2 mb-6">
          {dashboardData.estatisticas.map(e => (
            <div
              key={e.tipo}
              className="bg-gray-50 border rounded px-4 py-2 min-w-[120px]"
            >
              <div>
                <b>
                  {e.tipo === 'empresa'
                    ? 'Empresas sem instagram'
                    : e.tipo === 'pessoa'
                      ? 'Pessoas sem instagram'
                      : 'Advogados sem instagram'}
                </b>
                : {e.quantidade_sem_instagram}
              </div>
              <div className="text-xs text-gray-600">
                com Instagram: <b>{e.quantidade_com_instagram}</b>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Botões de Carregamento Manual */}
      <div className="flex flex-wrap gap-4 mb-6">
        <Button onClick={carregarDashboardData} disabled={loadingDashboard}>
          {loadingDashboard ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : null}
          Atualizar Estatísticas / Buscas
        </Button>
        <Button onClick={carregarEntidades} disabled={loadingEntidades}>
          {loadingEntidades ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : null}
          Exibir Lista de Entidades
        </Button>
      </div>

      {/* Card: Busca por Identificador */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center">
            <UserSearch className="mr-2 h-5 w-5" />
            Busca Instagram
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            <div>
              <label
                htmlFor="identifierType"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Tipo de Entidade
              </label>
              <Select
                value={identifierSearchType}
                onValueChange={(
                  value: 'empresa' | 'pessoa' | 'advogado' | ''
                ) => setIdentifierSearchType(value)}
              >
                <SelectTrigger id="identifierType">
                  <SelectValue placeholder="Selecione o tipo" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="empresa">Empresa</SelectItem>
                  <SelectItem value="pessoa">Pessoa Física</SelectItem>
                  <SelectItem value="advogado">Advogado(a)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="md:col-span-1">
              <label
                htmlFor="identifierValue"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                CNPJ PARA EMPRESA, CPF PARA PESSOA FÍSICA, ou OAB PARA
                ADVOGADO(A)
              </label>
              <Input
                id="identifierValue"
                type="text"
                placeholder="Digite o CPF, CNPJ ou OAB"
                value={identifierSearchValue}
                onChange={e => setIdentifierSearchValue(e.target.value)}
              />
            </div>
            <Button
              onClick={handleIdentifierSearch}
              disabled={loadingIdentifierSearch}
              className="w-full md:w-auto"
            >
              {loadingIdentifierSearch ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Search className="mr-2 h-4 w-4" />
              )}
              Buscar Identificador
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Botão para Buscar Todos Pendentes e específicos */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-lg flex items-center">
            <Play className="mr-2 h-5 w-5" /> Iniciar Busca Geral
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600 mb-4">
            Inicia a busca por perfis do Instagram para todas as entidades
            (empresas, pessoas, advogados) que ainda não possuem um perfil
            associado ou estão pendentes.
          </p>
          <div className="flex flex-col sm:flex-row gap-2 mb-2">
            <Button
              onClick={handleBuscarTodos}
              disabled={loadingBuscaTodos || loadingBulkResults}
              className="w-full sm:w-auto"
            >
              {loadingBuscaTodos ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Search className="mr-2 h-4 w-4" />
              )}
              {loadingBuscaTodos ? 'Buscando...' : 'Buscar Todos Pendentes'}
            </Button>
            <Button
              onClick={() => handleBuscarPendentesTipo('empresa')}
              disabled={loadingBuscaTodos || loadingBulkResults}
              className="w-full sm:w-auto"
            >
              <Building className="mr-2 h-4 w-4" /> Empresas Pendentes
            </Button>
            <Button
              onClick={() => handleBuscarPendentesTipo('pessoa')}
              disabled={loadingBuscaTodos || loadingBulkResults}
              className="w-full sm:w-auto"
            >
              <Users className="mr-2 h-4 w-4" /> Pessoas Pendentes
            </Button>
            <Button
              onClick={() => handleBuscarPendentesTipo('advogado')}
              disabled={loadingBuscaTodos || loadingBulkResults}
              className="w-full sm:w-auto"
            >
              <Briefcase className="mr-2 h-4 w-4" /> Advogados Pendentes
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Seção para exibir Resultados da Busca em Massa */}
      {loadingBulkResults && (
        <div className="text-center p-4">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto" />
          <p className="mt-2 text-sm text-gray-600">
            Processando busca em massa...
          </p>
        </div>
      )}
      {bulkResults && (
        <Card className="mb-6 bg-gray-50">
          <CardHeader>
            <CardTitle className="text-lg flex items-center">
              <List className="mr-2 h-5 w-5" /> Resultados da Busca Geral
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {Object.entries(bulkResults).map(par => {
              const [tipo, resultados] = par as [
                keyof BulkResultState,
                ResultadoBusca[],
              ];
              return (
                <div key={tipo} className="p-3 border rounded bg-white">
                  <h3 className="font-semibold capitalize flex items-center mb-2">
                    {tipo === 'empresas' ? (
                      <Building className="mr-2 h-5 w-5" />
                    ) : tipo === 'pessoas' ? (
                      <Users className="mr-2 h-5 w-5" />
                    ) : (
                      <Briefcase className="mr-2 h-5 w-5" />
                    )}
                    {tipo.charAt(0).toUpperCase() + tipo.slice(1)}:{' '}
                    {resultados.length} entidade(s) processada(s)
                  </h3>
                  {resultados.length > 0 && (
                    <ul className="list-none pl-0 text-sm space-y-4">
                      {resultados
                        .filter(
                          (res: any) =>
                            res.validated_profile ||
                            (res.possible_profiles &&
                              res.possible_profiles.length > 0)
                        )
                        .map((res: any, index: number) => (
                          <li
                            key={`${tipo} - res - ${index}`}
                            className="border-b pb-2 mb-2"
                          >
                            <div className="font-medium">
                              {res.entity?.nome ||
                                res.entity?.firstname +
                                  ' ' +
                                  res.entity?.lastname ||
                                res.entity?.razao_social ||
                                '(Sem nome)'}
                            </div>
                            {res.error && (
                              <div className="text-red-600">
                                Erro: {res.error}
                              </div>
                            )}
                            {res.validated_profile && (
                              <div className="mt-1 flex items-center gap-2 text-green-700 text-xs">
                                <Image
                                  src={`${API_URL} / proxy / instagram - image ? url = ${encodeURIComponent(
                                    res.validated_profile.perfil.profile_pic_url
                                  )} `}
                                  alt={res.validated_profile.perfil.username}
                                  width={40}
                                  height={40}
                                  className="rounded-full"
                                />
                                {editandoInstagram &&
                                editandoInstagram.tipo === tipo &&
                                editandoInstagram.index === index ? (
                                  <>
                                    <input
                                      value={valorInstagramManual}
                                      onChange={e =>
                                        setValorInstagramManual(e.target.value)
                                      }
                                      placeholder="@instagram"
                                      className="max-w-xs border rounded px-2 py-1 text-black"
                                    />
                                    <Button
                                      size="sm"
                                      onClick={() =>
                                        handleConfirmarInstagramManual(
                                          tipo,
                                          res,
                                          index
                                        )
                                      }
                                    >
                                      Salvar
                                    </Button>
                                    <Button
                                      size="sm"
                                      variant="outline"
                                      onClick={() => setEditandoInstagram(null)}
                                    >
                                      Cancelar
                                    </Button>
                                  </>
                                ) : (
                                  <>
                                    Perfil validado:{' '}
                                    <b>
                                      @{res.validated_profile.perfil.username}
                                    </b>
                                    <Button
                                      size="sm"
                                      variant="outline"
                                      onClick={() => {
                                        setEditandoInstagram({ tipo, index });
                                        setValorInstagramManual(
                                          res.validated_profile.perfil.username
                                        );
                                      }}
                                    >
                                      Editar
                                    </Button>
                                  </>
                                )}
                              </div>
                            )}
                            {res.possible_profiles &&
                              res.possible_profiles.length > 0 &&
                              !res.validated_profile && (
                                <div className="mt-1">
                                  <div className="text-xs text-gray-600">
                                    Possíveis perfis:{' '}
                                    {res.possible_profiles.join(', ')}
                                  </div>
                                  {editandoInstagram &&
                                  editandoInstagram.tipo === tipo &&
                                  editandoInstagram.index === index ? (
                                    <div className="flex gap-2 mt-2">
                                      <Input
                                        value={valorInstagramManual}
                                        onChange={e =>
                                          setValorInstagramManual(
                                            e.target.value
                                          )
                                        }
                                        placeholder="@instagram"
                                        className="max-w-xs"
                                      />
                                      <Button
                                        size="sm"
                                        onClick={() =>
                                          handleConfirmarInstagramManual(
                                            tipo,
                                            res,
                                            index
                                          )
                                        }
                                      >
                                        Confirmar
                                      </Button>
                                      <Button
                                        size="sm"
                                        variant="outline"
                                        onClick={() =>
                                          setEditandoInstagram(null)
                                        }
                                      >
                                        Cancelar
                                      </Button>
                                    </div>
                                  ) : (
                                    <Button
                                      size="sm"
                                      className="mt-2"
                                      onClick={() => {
                                        setEditandoInstagram({ tipo, index });
                                        setValorInstagramManual(
                                          res.possible_profiles[0] || ''
                                        );
                                      }}
                                    >
                                      Validar Instagram
                                    </Button>
                                  )}
                                </div>
                              )}
                            {res.candidates && res.candidates.length > 0 && (
                              <div className="mt-1">
                                <span className="text-xs font-semibold">
                                  Candidatos:
                                </span>
                                <ul className="list-disc pl-5">
                                  {res.candidates.map((cand: any) => (
                                    <li
                                      key={cand.pk}
                                      className="flex items-center gap-2"
                                    >
                                      <Image
                                        src={`${API_URL} /api/v1 / proxy / instagram - image ? url = ${encodeURIComponent(cand.profile_pic_url)} `}
                                        alt={cand.username}
                                        width={40}
                                        height={40}
                                        className="rounded-full"
                                      />
                                      <a
                                        href={`https://instagram.com/${cand.username}`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-blue-600 hover:underline"
                                      >
                                        @{cand.username}
                                      </a>
                                      <span className="text-xs text-gray-500">
                                        {cand.full_name}
                                      </span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </li>
                        ))}
                    </ul>
                  )}
                </div>
              );
            })}
          </CardContent>
        </Card>
      )}

      {/* Busca Avançada de Entidades */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Search className="mr-2 h-5 w-5" /> Verificar Status de Instagram
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-2 items-end mb-2">
            <Select
              value={tipoBusca}
              onValueChange={v =>
                setTipoBusca(v as 'empresa' | 'pessoa' | 'advogado')
              }
            >
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Tipo" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="empresa">Empresa</SelectItem>
                <SelectItem value="pessoa">Pessoa</SelectItem>
                <SelectItem value="advogado">Advogado</SelectItem>
              </SelectContent>
            </Select>
            <Input
              placeholder="Digite nome, CNPJ ou CPF"
              value={termoBusca}
              onChange={e => setTermoBusca(e.target.value)}
              className="max-w-xs"
            />
            <label className="text-sm">Limite:</label>
            <select
              value={limiteBusca}
              onChange={e => {
                setLimiteBusca(Number(e.target.value));
                setPaginaBusca(1);
                setInputPaginaBusca('1');
              }}
              className="border rounded px-2 py-1"
            >
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
            </select>
            <Button
              onClick={() => handleBuscaAvancada(1, limiteBusca)}
              disabled={loadingBuscaAvancada}
              className="w-full sm:w-auto"
            >
              {loadingBuscaAvancada ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Search className="mr-2 h-4 w-4" />
              )}
              Buscar
            </Button>
          </div>
          <EntitiesTable
            data={resultadosBusca}
            onSearchIndividual={handleSearchIndividual}
            isLoading={loadingBuscaAvancada}
            tipo={tipoBusca}
          />
          {totalBusca > 0 && (
            <div className="flex flex-wrap items-center justify-end mt-2 gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  if (paginaBusca > 1)
                    handleBuscaAvancada(paginaBusca - 1, limiteBusca);
                }}
                disabled={paginaBusca === 1}
              >
                Anterior
              </Button>
              <span className="text-sm self-center">
                Página {paginaBusca} de {numPaginasBusca}
              </span>
              <Input
                type="number"
                min={1}
                max={numPaginasBusca}
                value={inputPaginaBusca}
                onChange={e => setInputPaginaBusca(e.target.value)}
                className="w-16"
              />
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  const n = Math.max(
                    1,
                    Math.min(numPaginasBusca, Number(inputPaginaBusca))
                  );
                  handleBuscaAvancada(n, limiteBusca);
                }}
                disabled={Number(inputPaginaBusca) === paginaBusca}
              >
                Ir
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  if (paginaBusca < numPaginasBusca)
                    handleBuscaAvancada(paginaBusca + 1, limiteBusca);
                }}
                disabled={paginaBusca === numPaginasBusca}
              >
                Próxima
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Abas: Lista de Entidades e Últimas Buscas */}
      <Tabs defaultValue="lista" className="space-y-4">
        <TabsList>
          <TabsTrigger value="lista">Lista de Entidades</TabsTrigger>
        </TabsList>

        {/* Conteúdo da Aba: Lista de Entidades */}
        <TabsContent value="lista" className="space-y-4">
          {entidadesCarregadas || loadingEntidades ? (
            <div className="space-y-8">
              {/* Tabela de Empresas */}
              <Card>
                <CardHeader>
                  <CardTitle>Empresas</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-col sm:flex-row gap-2 mb-2 items-center">
                    <Input
                      placeholder="Buscar empresa..."
                      value={buscaEmpresa}
                      onChange={e => {
                        setBuscaEmpresa(e.target.value);
                      }}
                      className="max-w-xs"
                    />
                    <label className="text-sm">Limite:</label>
                    <select
                      value={limiteEmpresa}
                      onChange={e => {
                        setLimiteEmpresa(Number(e.target.value));
                        setPaginaEmpresa(1);
                        setInputPaginaEmpresa('1');
                      }}
                      className="border rounded px-2 py-1"
                    >
                      <option value={10}>10</option>
                      <option value={20}>20</option>
                      <option value={50}>50</option>
                    </select>
                  </div>
                  <EntitiesTable
                    data={empresas.filter(e =>
                      e.nome.toLowerCase().includes(buscaEmpresa.toLowerCase())
                    )}
                    onSearchIndividual={handleSearchIndividual}
                    isLoading={loadingEntidades}
                    tipo="empresa"
                  />
                  <div className="flex flex-wrap items-center justify-end mt-2 gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setPaginaEmpresa(p => Math.max(1, p - 1));
                        setInputPaginaEmpresa(p =>
                          String(Math.max(1, Number(p) - 1))
                        );
                      }}
                      disabled={paginaEmpresa === 1}
                    >
                      Anterior
                    </Button>
                    <span className="text-sm self-center">
                      Página {paginaEmpresa} de {numPaginasEmpresas}
                    </span>
                    <Input
                      type="number"
                      min={1}
                      max={numPaginasEmpresas}
                      value={inputPaginaEmpresa}
                      onChange={e => setInputPaginaEmpresa(e.target.value)}
                      className="w-16"
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        const n = Math.max(
                          1,
                          Math.min(
                            numPaginasEmpresas,
                            Number(inputPaginaEmpresa)
                          )
                        );
                        setPaginaEmpresa(n);
                      }}
                      disabled={Number(inputPaginaEmpresa) === paginaEmpresa}
                    >
                      Ir
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setPaginaEmpresa(p =>
                          Math.min(numPaginasEmpresas, p + 1)
                        );
                        setInputPaginaEmpresa(p =>
                          String(Math.min(numPaginasEmpresas, Number(p) + 1))
                        );
                      }}
                      disabled={paginaEmpresa === numPaginasEmpresas}
                    >
                      Próxima
                    </Button>
                  </div>
                </CardContent>
              </Card>
              {/* Tabela de Pessoas */}
              <Card>
                <CardHeader>
                  <CardTitle>Pessoas</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-col sm:flex-row gap-2 mb-2 items-center">
                    <Input
                      placeholder="Buscar pessoa..."
                      value={buscaPessoa}
                      onChange={e => {
                        setBuscaPessoa(e.target.value);
                      }}
                      className="max-w-xs"
                    />
                    <label className="text-sm">Limite:</label>
                    <select
                      value={limitePessoa}
                      onChange={e => {
                        setLimitePessoa(Number(e.target.value));
                        setPaginaPessoa(1);
                        setInputPaginaPessoa('1');
                      }}
                      className="border rounded px-2 py-1"
                    >
                      <option value={10}>10</option>
                      <option value={20}>20</option>
                      <option value={50}>50</option>
                    </select>
                  </div>
                  <EntitiesTable
                    data={pessoas.filter(e =>
                      e.nome.toLowerCase().includes(buscaPessoa.toLowerCase())
                    )}
                    onSearchIndividual={handleSearchIndividual}
                    isLoading={loadingEntidades}
                    tipo="pessoa"
                  />
                  <div className="flex flex-wrap items-center justify-end mt-2 gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setPaginaPessoa(p => Math.max(1, p - 1));
                        setInputPaginaPessoa(p =>
                          String(Math.max(1, Number(p) - 1))
                        );
                      }}
                      disabled={paginaPessoa === 1}
                    >
                      Anterior
                    </Button>
                    <span className="text-sm self-center">
                      Página {paginaPessoa} de {numPaginasPessoas}
                    </span>
                    <Input
                      type="number"
                      min={1}
                      max={numPaginasPessoas}
                      value={inputPaginaPessoa}
                      onChange={e => setInputPaginaPessoa(e.target.value)}
                      className="w-16"
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        const n = Math.max(
                          1,
                          Math.min(numPaginasPessoas, Number(inputPaginaPessoa))
                        );
                        setPaginaPessoa(n);
                      }}
                      disabled={Number(inputPaginaPessoa) === paginaPessoa}
                    >
                      Ir
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setPaginaPessoa(p =>
                          Math.min(numPaginasPessoas, p + 1)
                        );
                        setInputPaginaPessoa(p =>
                          String(Math.min(numPaginasPessoas, Number(p) + 1))
                        );
                      }}
                      disabled={paginaPessoa === numPaginasPessoas}
                    >
                      Próxima
                    </Button>
                  </div>
                </CardContent>
              </Card>
              {/* Tabela de Advogados */}
              <Card>
                <CardHeader>
                  <CardTitle>Advogados</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-col sm:flex-row gap-2 mb-2 items-center">
                    <Input
                      placeholder="Buscar advogado..."
                      value={buscaAdvogado}
                      onChange={e => {
                        setBuscaAdvogado(e.target.value);
                      }}
                      className="max-w-xs"
                    />
                    <label className="text-sm">Limite:</label>
                    <select
                      value={limiteAdvogado}
                      onChange={e => {
                        setLimiteAdvogado(Number(e.target.value));
                        setPaginaAdvogado(1);
                        setInputPaginaAdvogado('1');
                      }}
                      className="border rounded px-2 py-1"
                    >
                      <option value={10}>10</option>
                      <option value={20}>20</option>
                      <option value={50}>50</option>
                    </select>
                  </div>
                  <EntitiesTable
                    data={advogados.filter(e =>
                      e.nome.toLowerCase().includes(buscaAdvogado.toLowerCase())
                    )}
                    onSearchIndividual={handleSearchIndividual}
                    isLoading={loadingEntidades}
                    tipo="advogado"
                  />
                  <div className="flex flex-wrap items-center justify-end mt-2 gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setPaginaAdvogado(p => Math.max(1, p - 1));
                        setInputPaginaAdvogado(p =>
                          String(Math.max(1, Number(p) - 1))
                        );
                      }}
                      disabled={paginaAdvogado === 1}
                    >
                      Anterior
                    </Button>
                    <span className="text-sm self-center">
                      Página {paginaAdvogado} de {numPaginasAdvogados}
                    </span>
                    <Input
                      type="number"
                      min={1}
                      max={numPaginasAdvogados}
                      value={inputPaginaAdvogado}
                      onChange={e => setInputPaginaAdvogado(e.target.value)}
                      className="w-16"
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        const n = Math.max(
                          1,
                          Math.min(
                            numPaginasAdvogados,
                            Number(inputPaginaAdvogado)
                          )
                        );
                        setPaginaAdvogado(n);
                      }}
                      disabled={Number(inputPaginaAdvogado) === paginaAdvogado}
                    >
                      Ir
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setPaginaAdvogado(p =>
                          Math.min(numPaginasAdvogados, p + 1)
                        );
                        setInputPaginaAdvogado(p =>
                          String(Math.min(numPaginasAdvogados, Number(p) + 1))
                        );
                      }}
                      disabled={paginaAdvogado === numPaginasAdvogados}
                    >
                      Próxima
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <p className="text-gray-500">
              Clique em &quot;Carregar Lista de Entidades&quot; para ver a
              lista.
            </p>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
