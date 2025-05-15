"use client";
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2, Search, Building, Users, Briefcase } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { instagramService } from "../services/api";
import { useSearchParams } from 'next/navigation';

export default function BuscaRelacionadosPage() {
    const { toast } = useToast();
    const searchParams = useSearchParams();
    const [tipoRelacionado, setTipoRelacionado] = useState<'empresa' | 'pessoa' | 'advogado'>('empresa');
    const [idRelacionado, setIdRelacionado] = useState('');
    const [loadingRelated, setLoadingRelated] = useState(false);
    const [relatedResult, setRelatedResult] = useState<any>(null);
    const [resultadosRelacionados, setResultadosRelacionados] = useState<any[]>([]);
    const [instagramPrincipal, setInstagramPrincipal] = useState<string>('');
    const [loadingBuscaInstagram, setLoadingBuscaInstagram] = useState(false);
    const [manualNames, setManualNames] = useState('');
    const [manualInstagram, setManualInstagram] = useState('');
    const [manualResults, setManualResults] = useState<any[]>([]);
    const [perfilPrincipal, setPerfilPrincipal] = useState<any>(null);
    const [mensagemErro, setMensagemErro] = useState<string | null>(null);

    useEffect(() => {
        // Preencher campos se vierem na URL
        const id = searchParams.get('id');
        const type = searchParams.get('type');
        if (id) setIdRelacionado(id);
        if (type && ['empresa', 'pessoa', 'advogado'].includes(type)) setTipoRelacionado(type as any);
    }, [searchParams]);

    // Passo 1: Buscar Relacionados
    const handleBuscarRelacionados = async () => {
        if (!idRelacionado.trim()) {
            setMensagemErro('Identificador obrigatório: Insira o CPF, CNPJ ou OAB.');
            return;
        }
        // Limpa o campo para aceitar apenas números
        const idLimpo = idRelacionado.replace(/\D/g, '');
        setLoadingRelated(true);
        setRelatedResult(null);
        setResultadosRelacionados([]);
        setInstagramPrincipal('');
        setPerfilPrincipal(null);
        try {
            const data = await instagramService.getEntityRelated(tipoRelacionado, idLimpo);
            setRelatedResult(data);
            // Buscar Instagram da entidade principal
            try {
                const perfilPrincipal = await instagramService.getEntityProfile(tipoRelacionado, { identifier: idLimpo });
                setPerfilPrincipal(perfilPrincipal?.entity || null);
                const insta = perfilPrincipal?.validated_profile?.perfil?.username || perfilPrincipal?.entity?.instagram || '';
                setInstagramPrincipal(insta);
                setManualInstagram(insta);
            } catch (error: any) {
                const msg = error?.response?.data?.detail || error?.response?.data?.message || error?.message || 'Erro ao buscar perfil principal.';
                setMensagemErro(msg);
            }
            toast({ title: 'Relacionados carregados', description: 'Os relacionados foram encontrados.' });
        } catch (error: any) {
            console.log('ERRO CAPTURADO (relacionados):', error);
            toast({ title: 'Teste', description: 'Toast manual', variant: 'destructive' });
            const msg = error?.response?.data?.detail || error?.response?.data?.message || error?.message || 'Erro desconhecido ao buscar relacionados.';
            setMensagemErro(msg);
        } finally {
            setLoadingRelated(false);
        }
    };

    // Passo 2: Busca automática
    const handleBuscarInstagramRelacionados = async () => {
        if (!instagramPrincipal) {
            setMensagemErro('Instagram da entidade principal não encontrado. Cadastre manualmente ou busque.');
            return;
        }
        setLoadingBuscaInstagram(true);
        try {
            const nomesRelacionados = relatedResult.related_entities.map((rel: any) => [rel.firstname, rel.lastname].filter(Boolean).join(' ')).filter(Boolean);
            const resultadoBusca = await instagramService.searchNamesInFollowers(instagramPrincipal, nomesRelacionados, 0.8);
            const resultados = relatedResult.related_entities.map((rel: any, idx: number) => {
                const nomeBusca = nomesRelacionados[idx];
                const match = resultadoBusca.matches?.find((m: any) => m.name_searched === nomeBusca);
                return {
                    ...rel,
                    status: 'Busca aprofundada',
                    resultado: match ? { matches: [match] } : { matches: [] }
                };
            });
            setResultadosRelacionados(resultados);
            toast({ title: 'Busca automática concluída', description: 'Resultados exibidos abaixo.' });
        } catch (error: any) {
            console.log('ERRO CAPTURADO (busca automática):', error);
            const msg = error?.response?.data?.detail || error?.response?.data?.message || error?.message || 'Erro desconhecido na busca automática.';
            setMensagemErro(msg);
        } finally {
            setLoadingBuscaInstagram(false);
        }
    };

    // Passo 3: Busca manual
    const handleBuscaManual = async () => {
        if (!manualInstagram.trim() || !manualNames.trim()) {
            setMensagemErro('Preencha o Instagram e pelo menos um nome.');
            return;
        }
        setLoadingBuscaInstagram(true);
        try {
            const nomes = manualNames.split(',').map(n => n.trim()).filter(Boolean);
            const resultadoBusca = await instagramService.searchNamesInFollowers(manualInstagram.trim(), nomes, 0.8);
            setManualResults(resultadoBusca.found_names || []);
            toast({ title: 'Busca manual concluída', description: 'Veja os resultados abaixo.' });
        } catch (error: any) {
            console.log('ERRO CAPTURADO (busca manual):', error);
            const msg = error?.response?.data?.detail || error?.response?.data?.message || error?.message || 'Erro desconhecido na busca manual.';
            setMensagemErro(msg);
        } finally {
            setLoadingBuscaInstagram(false);
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
            <h1 className="text-3xl font-bold mb-6">Busca de Relacionados</h1>
            {/* Passo 1: Buscar Relacionados */}
            <Card className="mb-6">
                <CardHeader>
                    <CardTitle>Buscar Relacionados</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex flex-col sm:flex-row gap-2 items-end">
                        <Select value={tipoRelacionado} onValueChange={v => setTipoRelacionado(v as 'empresa' | 'pessoa' | 'advogado')}>
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
                            placeholder="Digite o CPF ou CNPJ"
                            value={idRelacionado}
                            onChange={e => setIdRelacionado(e.target.value)}
                            className="max-w-xs"
                        />
                        <Button onClick={handleBuscarRelacionados} disabled={loadingRelated}>
                            {loadingRelated ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Search className="mr-2 h-4 w-4" />}
                            Buscar Relacionados
                        </Button>
                    </div>
                </CardContent>
            </Card>
            {/* Exibe lista de relacionados */}
            {relatedResult && (
                <Card className="mb-6">
                    <CardHeader>
                        <CardTitle>Relacionados Encontrados</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid gap-3 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
                            {relatedResult.related_entities.map((rel: any, idx: number) => (
                                <div key={idx} className="border rounded-lg p-4 bg-white shadow flex flex-col gap-2">
                                    <div className="flex items-center gap-2 mb-1">
                                        {rel.type === 'empresa' && <Building className="h-5 w-5 text-blue-700" />}
                                        {rel.type === 'pessoa' && <Users className="h-5 w-5 text-green-700" />}
                                        {rel.type === 'advogado' && <Briefcase className="h-5 w-5 text-yellow-700" />}
                                        <span className="font-semibold text-base">{(rel.firstname && rel.lastname) ? `${rel.firstname} ${rel.lastname}` : rel.firstname || rel.nome || rel.razao_social || rel.full_name || '(Sem nome)'}</span>
                                    </div>
                                    <div className="text-xs text-gray-600">
                                        {rel.cpf && <>CPF: <span className="font-mono">{rel.cpf}</span></>}
                                        {rel.cnpj && <>CNPJ: <span className="font-mono">{rel.cnpj}</span></>}
                                        {rel.oab && <span className="ml-2">OAB: {rel.oab}</span>}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}
            {/* Card com dados da entidade principal */}
            {perfilPrincipal && (
                <Card className="mb-6">
                    <CardHeader>
                        <CardTitle>Entidade Consultada</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <p className="text-sm font-medium text-gray-500">Nome/Razão Social</p>
                                <p className="font-semibold text-lg">{
                                    perfilPrincipal.tipo === 'advogado' || perfilPrincipal.tipo === 'pessoa'
                                        ? [perfilPrincipal.firstname, perfilPrincipal.lastname].filter(Boolean).join(' ')
                                        : perfilPrincipal.razao_social || perfilPrincipal.nome
                                }</p>
                            </div>
                            <div>
                                <p className="text-sm font-medium text-gray-500">Tipo</p>
                                <p className="font-semibold capitalize">{perfilPrincipal.tipo}</p>
                            </div>
                            {perfilPrincipal.cnpj && (
                                <div>
                                    <p className="text-sm font-medium text-gray-500">CNPJ</p>
                                    <p className="font-semibold">{perfilPrincipal.cnpj}</p>
                                </div>
                            )}
                            {perfilPrincipal.cpf && (
                                <div>
                                    <p className="text-sm font-medium text-gray-500">CPF</p>
                                    <p className="font-semibold">{perfilPrincipal.cpf}</p>
                                </div>
                            )}
                            {perfilPrincipal.oab && (
                                <div>
                                    <p className="text-sm font-medium text-gray-500">OAB</p>
                                    <p className="font-semibold">{perfilPrincipal.oab}</p>
                                </div>
                            )}
                            <div>
                                <p className="text-sm font-medium text-gray-500">Instagram</p>
                                <p className="font-semibold">{instagramPrincipal || 'Não informado'}</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}
            {/* Passo 2: Busca automática */}
            {relatedResult && (
                <Card className="mb-6">
                    <CardHeader>
                        <CardTitle>Busca Automática de Instagram dos Relacionados</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex gap-2 mb-2">
                            <Input
                                placeholder="@instagram da empresa"
                                value={instagramPrincipal}
                                onChange={e => setInstagramPrincipal(e.target.value)}
                                className="max-w-xs"
                            />
                            <Button onClick={handleBuscarInstagramRelacionados} disabled={loadingBuscaInstagram}>
                                {loadingBuscaInstagram ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Search className="mr-2 h-4 w-4" />}
                                Buscar Instagram dos Relacionados
                            </Button>
                        </div>
                        {resultadosRelacionados.length > 0 && (
                            <div className="grid gap-3 grid-cols-1 md:grid-cols-2 lg:grid-cols-3 mt-2">
                                {resultadosRelacionados.map((rel, idx) => (
                                    <div key={idx} className="border rounded-lg p-4 bg-white shadow flex flex-col gap-2">
                                        <div className="font-semibold">{rel.firstname} {rel.lastname}</div>
                                        <div className="text-xs text-gray-600">{rel.type} {rel.oab && <>OAB: {rel.oab}</>}</div>
                                        {rel.status === 'Busca aprofundada' && (
                                            <div className="mt-2">
                                                {rel.resultado && rel.resultado.matches && rel.resultado.matches.length > 0 ? (
                                                    <div className="bg-green-50 border border-green-200 rounded p-2">
                                                        <div className="text-green-700 font-medium">Encontrado entre seguidores!</div>
                                                        <ul className="mt-1 space-y-1">
                                                            {rel.resultado.matches.map((match: any, i: number) => (
                                                                <li key={i} className="flex items-center gap-2">
                                                                    <img
                                                                        src={match.profile_pic_url || '/img/placeholder_profile.png'}
                                                                        alt={match.username}
                                                                        className="w-8 h-8 rounded-full border"
                                                                        onError={e => { (e.currentTarget as HTMLImageElement).src = '/img/placeholder_profile.png'; }}
                                                                    />
                                                                    <a href={`https://instagram.com/${match.username}`} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">@{match.username}</a>
                                                                    <span className="text-xs text-gray-600">{match.full_name}</span>
                                                                </li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                ) : (
                                                    <div className="bg-yellow-50 border border-yellow-200 rounded p-2 text-yellow-700">Não encontrado entre os seguidores.</div>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>
            )}
            {/* Passo 3: Busca manual */}
            <Card className="mb-6">
                <CardHeader>
                    <CardTitle>Busca Profunda entre Seguidores -Apenas Perfis Públicos-</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex flex-col sm:flex-row gap-2 mb-2 items-end">
                        <Input
                            placeholder="Nomes para buscar (separados por vírgula)"
                            value={manualNames}
                            onChange={e => setManualNames(e.target.value)}
                            className="max-w-xs"
                        />
                        <Input
                            placeholder="@instagram alvo"
                            value={manualInstagram}
                            onChange={e => setManualInstagram(e.target.value)}
                            className="max-w-xs"
                        />
                        <Button onClick={handleBuscaManual} disabled={loadingBuscaInstagram}>
                            {loadingBuscaInstagram ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Search className="mr-2 h-4 w-4" />}
                            Buscar Manualmente
                        </Button>
                    </div>
                    {manualResults.length > 0 && (
                        <div className="mt-2">
                            <div className="font-semibold mb-2">Resultados da Busca Manual:</div>
                            <ul className="space-y-2">
                                {manualResults.map((match: any, i: number) => (
                                    <li key={i} className="flex items-center gap-2">
                                        <a href={match.profile_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                                            @{match.username}
                                        </a>
                                        <span className="text-xs text-gray-600">{match.matched_name}</span>
                                        <span className="text-xs text-gray-600">({match.similarity}%)</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
} 