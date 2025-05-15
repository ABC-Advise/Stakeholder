'use client';

import React, { useState, useCallback, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { RefreshCw, Check, X, MessageSquare, Loader2, Info, Edit, Save } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { instagramService, type ResultadoBusca, type Candidato, type ValidatedProfile, type Entidade } from "../../services/api";

const API_URL = process.env.NEXT_PUBLIC_INSTAGRAM_API_URL;

export default function ResultadoBuscaPage() {
    const params = useParams();
    const router = useRouter();
    const { toast } = useToast();

    const entityType = params.entity_type as string;
    const entityId = params.entity_id as string;

    const [loading, setLoading] = useState(true);
    const [resultado, setResultado] = useState<ResultadoBusca | null>(null);
    const [validatingPk, setValidatingPk] = useState<number | null>(null);
    const [loadingNovaBusca, setLoadingNovaBusca] = useState(false);
    const [usernameParaConfirmar, setUsernameParaConfirmar] = useState('');
    const [isSaving, setIsSaving] = useState(false);
    const [mensagemErro, setMensagemErro] = useState<string | null>(null);

    const carregarResultados = useCallback(async () => {
        if (!entityType || !entityId) {
            setMensagemErro('Tipo ou ID da entidade ausentes na URL.');
            setLoading(false);
            return;
        }
        setLoading(true);
        setUsernameParaConfirmar('');
        try {
            const data = await instagramService.getEntityProfile(entityType as 'empresa' | 'pessoa' | 'advogado', { identifier: entityId });
            if (data) {
                setResultado(data);
                const currentInstagram = data.validated_profile?.perfil.username || (data.entity as Entidade).instagram;
                if (currentInstagram) {
                    setUsernameParaConfirmar(currentInstagram);
                } else {
                    setUsernameParaConfirmar('');
                }
            } else {
                setResultado(null);
                setMensagemErro('Entidade não encontrada. Não foi possível encontrar os dados para esta entidade.');
            }
        } catch (error: any) {
            let msg = error?.response?.data?.detail || error?.response?.data?.message || error?.message || 'Erro ao carregar resultados.';
            setMensagemErro(msg);
            setResultado(null);
        } finally {
            setLoading(false);
        }
    }, [entityType, entityId, toast]);

    useEffect(() => {
        carregarResultados();
    }, [carregarResultados]);

    const handleConfirmarPerfil = async () => {
        if (!entityType || !entityId) return;
        const usernameToSave = usernameParaConfirmar.trim();
        if (!usernameToSave) {
            setMensagemErro('Por favor, informe um nome de usuário do Instagram para salvar.');
            return;
        }
        setIsSaving(true);
        try {
            await instagramService.confirmInstagramProfile(entityType, entityId, usernameToSave);
            await carregarResultados();
        } catch (error: any) {
            let mensagemErro = error?.response?.data?.detail || error?.response?.data?.message || error?.message || 'Não foi possível salvar o perfil para a entidade.';
            setMensagemErro(mensagemErro);
        } finally {
            setIsSaving(false);
        }
    };

    const handleNovaBusca = async () => {
        if (!entityType || !entityId) return;
        setLoadingNovaBusca(true);
        try {
            await instagramService.findInstagramForEntity(entityType, entityId);
            setResultado(null);
            setUsernameParaConfirmar('');
        } catch (error: any) {
            setMensagemErro(error?.response?.data?.detail || error?.response?.data?.message || error?.message || 'Não foi possível iniciar uma nova busca.');
        } finally {
            setLoadingNovaBusca(false);
        }
    };

    if (loading) {
        return (
            <div className="container mx-auto py-6 space-y-6">
                <div className="flex justify-between items-center mb-6">
                    <div className='h-8 bg-gray-200 rounded animate-pulse w-1/3'></div>
                    <div className='h-10 bg-gray-200 rounded animate-pulse w-32'></div>
                </div>
                <div className='h-32 bg-gray-200 rounded animate-pulse'></div>
                <div className='h-64 bg-gray-200 rounded animate-pulse'></div>
            </div>
        );
    }

    if (!resultado) {
        return (
            <div className="container mx-auto py-6 text-center space-y-4">
                <h1 className="text-3xl font-bold">Resultados da Busca</h1>
                <p className="text-xl text-red-600">Erro ao carregar os dados.</p>
                <Button onClick={carregarResultados} variant="outline" className="mr-2">
                    Tentar Novamente
                </Button>
                <Button onClick={() => router.back()} variant="outline">Voltar</Button>
            </div>
        );
    }

    const ValidatedProfileDisplay = ({ profile, score }: { profile: ValidatedProfile['perfil'], score: number }) => (
        <div className="flex items-center space-x-4 p-4 border rounded-lg bg-gray-50">
            <img
                src={`${API_URL}/proxy/instagram-image?url=${encodeURIComponent(profile.profile_pic_url)}`}
                alt={`Perfil de ${profile.username}`}
                className="w-16 h-16 rounded-full object-cover border"
                onError={(e: React.SyntheticEvent<HTMLImageElement, Event>) => e.currentTarget.src = '/img/placeholder_profile.png'}
            />
            <div className="flex-grow">
                <a
                    href={`https://instagram.com/${profile.username}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-semibold text-lg text-blue-600 hover:underline"
                >
                    @{profile.username}
                </a>
                <p className="text-md font-medium">{profile.full_name}</p>
                {profile.bio && <p className="text-sm text-gray-600 mt-1">{profile.bio}</p>}
                <p className="text-sm font-medium mt-1">Score: <Badge variant={score > 80 ? "default" : score > 50 ? "secondary" : "destructive"}>{score}%</Badge></p>
            </div>
            <Button
                onClick={() => setUsernameParaConfirmar(profile.username)}
                size="sm"
                variant="outline"
                title="Editar este perfil no campo abaixo"
            >
                <Edit className="mr-2 h-4 w-4" />
                Editar
            </Button>
        </div>
    );

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
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">Resultados da Busca</h1>
                <Button onClick={handleNovaBusca} disabled={loadingNovaBusca}>
                    {loadingNovaBusca ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <RefreshCw className="mr-2 h-4 w-4" />}
                    {loadingNovaBusca ? 'Iniciando...' : 'Solicitar Nova Busca'}
                </Button>
            </div>

            <Card className="mb-6 bg-white shadow">
                <CardHeader>
                    <CardTitle>Informações da Entidade</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <p className="text-sm font-medium text-gray-500">Nome/Razão Social</p>
                            <p className="font-semibold text-lg">{(resultado.entity as Entidade).razao_social || (resultado.entity as Entidade).nome}</p>
                        </div>
                        <div>
                            <p className="text-sm font-medium text-gray-500">Tipo</p>
                            <p className="font-semibold capitalize">{(resultado.entity as Entidade).tipo}</p>
                        </div>
                        {(resultado.entity as Entidade).cnpj && (
                            <div>
                                <p className="text-sm font-medium text-gray-500">CNPJ</p>
                                <p className="font-semibold">{(resultado.entity as Entidade).cnpj}</p>
                            </div>
                        )}
                        {(resultado.entity as Entidade).cpf && (
                            <div>
                                <p className="text-sm font-medium text-gray-500">CPF</p>
                                <p className="font-semibold">{(resultado.entity as Entidade).cpf}</p>
                            </div>
                        )}
                    </div>
                </CardContent>
            </Card>

            {resultado.validated_profile && (
                <Card className="mb-6 bg-green-50 border-green-200 shadow">
                    <CardHeader>
                        <CardTitle className="text-green-800 flex items-center">
                            <Check className="mr-2 h-5 w-5" /> Perfil Atual da Entidade
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ValidatedProfileDisplay profile={resultado.validated_profile.perfil} score={resultado.validated_profile.score} />
                    </CardContent>
                </Card>
            )}

            <Card className="mb-6 bg-blue-50 border-blue-200 shadow">
                <CardHeader>
                    <CardTitle className="text-blue-800 flex items-center">
                        <Save className="mr-2 h-5 w-5" /> Confirmar/Inserir Instagram para a Entidade
                    </CardTitle>
                </CardHeader>
                <CardContent className="flex flex-col sm:flex-row items-center space-y-2 sm:space-y-0 sm:space-x-4">
                    <Input
                        placeholder="Digite ou selecione o @username"
                        value={usernameParaConfirmar}
                        onChange={(e) => setUsernameParaConfirmar(e.target.value)}
                        className="flex-grow"
                    />
                    <Button onClick={handleConfirmarPerfil} disabled={isSaving} className="w-full sm:w-auto">
                        {isSaving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                        Salvar Instagram
                    </Button>
                </CardContent>
            </Card>

            <Card className="bg-white shadow">
                <CardHeader>
                    <CardTitle>Sugestões de Perfis (Candidatos)</CardTitle>
                </CardHeader>
                <CardContent>
                    {resultado.candidates.length === 0 ? (
                        <p className="text-sm text-gray-500 text-center py-4">Nenhum candidato sugerido encontrado.</p>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead className="w-[80px]">Imagem</TableHead>
                                    <TableHead>Perfil Instagram</TableHead>
                                    <TableHead>Nome no Perfil</TableHead>
                                    <TableHead>Bio</TableHead>
                                    <TableHead className="text-right">Ação</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {resultado.candidates.map((candidato: Candidato) => (
                                    <TableRow key={candidato.pk}>
                                        <TableCell>
                                            <img
                                                src={candidato.profile_pic_url || 'https://via.placeholder.com/40'}
                                                alt={`Perfil de ${candidato.username}`}
                                                className="w-10 h-10 rounded-full object-cover border"
                                                onError={(e: React.SyntheticEvent<HTMLImageElement, Event>) => e.currentTarget.src = 'https://via.placeholder.com/40'}
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <a
                                                href={`https://instagram.com/${candidato.username}`}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="font-medium text-blue-600 hover:underline"
                                            >
                                                @{candidato.username}
                                            </a>
                                        </TableCell>
                                        <TableCell>{candidato.full_name}</TableCell>
                                        <TableCell className="text-sm text-gray-600 max-w-xs truncate" title={candidato.bio}>{candidato.bio || "-"} </TableCell>
                                        <TableCell className="text-right">
                                            <Button
                                                size="sm"
                                                variant="ghost"
                                                onClick={() => setUsernameParaConfirmar(candidato.username)}
                                                title="Usar este username no campo de confirmação"
                                                className="text-blue-600 hover:bg-blue-50"
                                            >
                                                <Edit className="mr-1 h-4 w-4" />
                                                Usar este
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>
        </div>
    );
} 