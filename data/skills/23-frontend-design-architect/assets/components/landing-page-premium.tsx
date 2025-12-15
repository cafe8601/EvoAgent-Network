/**
 * Premium Landing Page Components
 * 
 * AI 생성처럼 보이지 않는 프리미엄 랜딩 페이지 컴포넌트 모음
 * 
 * 주요 원칙:
 * - 비대칭 레이아웃 (60/40)
 * - 솔리드 배경 (그라디언트 최소화)
 * - 8pt 그리드 스페이싱
 * - 1-2개 폰트 최대
 * - 미세한 그림자 (shadow-sm/md)
 */

import React, { useState } from 'react';
import { ChevronDown, Zap, Shield, BarChart3, Check } from 'lucide-react';

// ============================================
// 1. HERO SECTION - 비대칭 레이아웃
// ============================================

interface HeroProps {
    badge?: string;
    headline: React.ReactNode;
    subheadline: string;
    primaryCTA: {
        text: string;
        onClick?: () => void;
    };
    secondaryCTA?: {
        text: string;
        onClick?: () => void;
    };
    socialProof?: {
        count: string;
        label: string;
        avatarCount?: number;
    };
    visual?: React.ReactNode;
    floatingCard?: {
        label: string;
        value: string;
    };
}

export function HeroAsymmetric({
    badge,
    headline,
    subheadline,
    primaryCTA,
    secondaryCTA,
    socialProof,
    visual,
    floatingCard
}: HeroProps) {
    return (
        <section className="relative bg-stone-50 overflow-hidden">
            <div className="max-w-7xl mx-auto px-6 lg:px-12 py-24 lg:py-32">
                <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
                    {/* 좌측: 콘텐츠 */}
                    <div>
                        {badge && (
                            <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-50 text-blue-700 text-sm font-medium rounded-full mb-6">
                                <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
                                {badge}
                            </div>
                        )}

                        <h1 className="text-5xl lg:text-6xl xl:text-7xl font-bold text-slate-900 leading-tight mb-6 tracking-tight">
                            {headline}
                        </h1>

                        <p className="text-lg lg:text-xl text-slate-600 mb-8 max-w-xl leading-relaxed">
                            {subheadline}
                        </p>

                        <div className="flex flex-col sm:flex-row gap-4">
                            <button
                                onClick={primaryCTA.onClick}
                                className="px-8 py-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 shadow-sm hover:shadow-md transition-all duration-150"
                            >
                                {primaryCTA.text}
                            </button>
                            {secondaryCTA && (
                                <button
                                    onClick={secondaryCTA.onClick}
                                    className="px-8 py-4 border-2 border-slate-300 text-slate-700 font-semibold rounded-lg hover:border-slate-400 transition-all duration-150"
                                >
                                    {secondaryCTA.text}
                                </button>
                            )}
                        </div>

                        {socialProof && (
                            <div className="mt-8 flex items-center gap-6">
                                <div className="flex -space-x-2">
                                    {[...Array(socialProof.avatarCount || 4)].map((_, i) => (
                                        <div
                                            key={i}
                                            className="w-10 h-10 rounded-full bg-slate-300 border-2 border-white"
                                            style={{ backgroundColor: `hsl(${210 + i * 20}, 30%, ${60 + i * 5}%)` }}
                                        />
                                    ))}
                                </div>
                                <div className="text-sm">
                                    <div className="font-semibold text-slate-900">{socialProof.count}</div>
                                    <div className="text-slate-600">{socialProof.label}</div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* 우측: 시각 요소 */}
                    <div className="relative lg:pl-8">
                        {visual ? (
                            visual
                        ) : (
                            <div className="relative rounded-xl overflow-hidden shadow-2xl border border-slate-200">
                                <div className="aspect-[4/3] bg-slate-100 flex items-center justify-center text-slate-400">
                                    Product Screenshot
                                </div>
                            </div>
                        )}

                        {floatingCard && (
                            <div className="absolute -bottom-6 -left-6 bg-white p-4 rounded-lg shadow-lg border border-slate-200">
                                <div className="text-sm text-slate-600 mb-1">{floatingCard.label}</div>
                                <div className="text-2xl font-bold text-green-600">{floatingCard.value}</div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </section>
    );
}

// ============================================
// 2. FEATURES SECTION - 3컬럼 그리드
// ============================================

interface Feature {
    icon: React.ElementType;
    title: string;
    description: string;
}

interface FeaturesProps {
    title: string;
    subtitle?: string;
    features: Feature[];
}

export function Features({ title, subtitle, features }: FeaturesProps) {
    return (
        <section className="py-24 lg:py-32 bg-white">
            <div className="max-w-7xl mx-auto px-6 lg:px-12">
                <div className="text-center mb-16">
                    <h2 className="text-4xl lg:text-5xl font-bold text-slate-900 mb-4">
                        {title}
                    </h2>
                    {subtitle && (
                        <p className="text-xl text-slate-600 max-w-2xl mx-auto">
                            {subtitle}
                        </p>
                    )}
                </div>

                <div className="grid md:grid-cols-3 gap-12">
                    {features.slice(0, 6).map((feature, i) => (
                        <div key={i} className="group">
                            <div className="w-12 h-12 rounded-lg bg-blue-50 flex items-center justify-center mb-6 group-hover:bg-blue-100 transition-colors">
                                <feature.icon className="w-6 h-6 text-blue-600" />
                            </div>

                            <h3 className="text-2xl font-bold text-slate-900 mb-3">
                                {feature.title}
                            </h3>

                            <p className="text-slate-600 leading-relaxed">
                                {feature.description}
                            </p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}

// ============================================
// 3. TESTIMONIALS - 정적 그리드 (캐러셀 아님!)
// ============================================

interface Testimonial {
    quote: string;
    author: string;
    role: string;
    company?: string;
    rating?: number;
    avatarUrl?: string;
}

interface TestimonialsProps {
    title: string;
    subtitle?: string;
    testimonials: Testimonial[];
    darkMode?: boolean;
}

export function Testimonials({ title, subtitle, testimonials, darkMode = true }: TestimonialsProps) {
    const bgClass = darkMode ? 'bg-slate-900' : 'bg-slate-50';
    const cardBgClass = darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200';
    const textClass = darkMode ? 'text-white' : 'text-slate-900';
    const mutedClass = darkMode ? 'text-slate-400' : 'text-slate-600';
    const quoteClass = darkMode ? 'text-slate-300' : 'text-slate-700';

    return (
        <section className={`py-24 ${bgClass}`}>
            <div className="max-w-7xl mx-auto px-6 lg:px-12">
                <div className="text-center mb-16">
                    <h2 className={`text-4xl lg:text-5xl font-bold ${textClass} mb-4`}>
                        {title}
                    </h2>
                    {subtitle && (
                        <p className={`text-xl ${mutedClass}`}>
                            {subtitle}
                        </p>
                    )}
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {testimonials.map((testimonial, i) => (
                        <div key={i} className={`${cardBgClass} rounded-xl p-8 border`}>
                            {testimonial.rating && (
                                <div className="flex gap-1 mb-4">
                                    {[...Array(testimonial.rating)].map((_, j) => (
                                        <svg key={j} className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                        </svg>
                                    ))}
                                </div>
                            )}

                            <p className={`${quoteClass} mb-6 leading-relaxed`}>
                                "{testimonial.quote}"
                            </p>

                            <div className="flex items-center gap-3">
                                <div
                                    className={`w-12 h-12 rounded-full ${darkMode ? 'bg-slate-700' : 'bg-slate-200'} flex items-center justify-center`}
                                >
                                    {testimonial.avatarUrl ? (
                                        <img src={testimonial.avatarUrl} alt={testimonial.author} className="w-full h-full rounded-full object-cover" />
                                    ) : (
                                        <span className={textClass}>{testimonial.author.charAt(0)}</span>
                                    )}
                                </div>
                                <div>
                                    <div className={`font-semibold ${textClass}`}>{testimonial.author}</div>
                                    <div className={`text-sm ${mutedClass}`}>
                                        {testimonial.role}
                                        {testimonial.company && `, ${testimonial.company}`}
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}

// ============================================
// 4. PRICING - 2-3 플랜 (4+ 금지)
// ============================================

interface PricingPlan {
    name: string;
    price: number;
    period?: string;
    description: string;
    features: string[];
    popular?: boolean;
    ctaText?: string;
}

interface PricingProps {
    title: string;
    subtitle?: string;
    plans: PricingPlan[];
}

export function Pricing({ title, subtitle, plans }: PricingProps) {
    return (
        <section className="py-24 bg-slate-50">
            <div className="max-w-7xl mx-auto px-6 lg:px-12">
                <div className="text-center mb-16">
                    <h2 className="text-4xl lg:text-5xl font-bold text-slate-900 mb-4">
                        {title}
                    </h2>
                    {subtitle && (
                        <p className="text-xl text-slate-600">
                            {subtitle}
                        </p>
                    )}
                </div>

                <div className={`grid gap-8 ${plans.length === 2 ? 'md:grid-cols-2 max-w-4xl mx-auto' : 'md:grid-cols-3'}`}>
                    {plans.slice(0, 3).map((plan, i) => (
                        <div
                            key={i}
                            className={`relative rounded-2xl p-8 ${plan.popular
                                    ? 'bg-slate-900 text-white ring-4 ring-blue-600 scale-105 z-10'
                                    : 'bg-white border border-slate-200'
                                }`}
                        >
                            {plan.popular && (
                                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                                    <div className="px-4 py-1 bg-blue-600 text-white text-sm font-semibold rounded-full">
                                        Most Popular
                                    </div>
                                </div>
                            )}

                            <div className="mb-6">
                                <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                                <p className={plan.popular ? 'text-slate-300' : 'text-slate-600'}>
                                    {plan.description}
                                </p>
                            </div>

                            <div className="mb-8">
                                <span className="text-5xl font-bold">${plan.price}</span>
                                <span className={plan.popular ? 'text-slate-300' : 'text-slate-600'}>
                                    /{plan.period || 'month'}
                                </span>
                            </div>

                            <button
                                className={`w-full py-3 rounded-lg font-semibold transition-colors mb-8 ${plan.popular
                                        ? 'bg-blue-600 text-white hover:bg-blue-700'
                                        : 'bg-slate-900 text-white hover:bg-slate-800'
                                    }`}
                            >
                                {plan.ctaText || 'Start Free Trial'}
                            </button>

                            <ul className="space-y-3">
                                {plan.features.map((feature, j) => (
                                    <li key={j} className="flex items-start gap-3">
                                        <Check
                                            className={`w-5 h-5 flex-shrink-0 mt-0.5 ${plan.popular ? 'text-blue-400' : 'text-green-600'
                                                }`}
                                        />
                                        <span className={plan.popular ? 'text-slate-300' : 'text-slate-600'}>
                                            {feature}
                                        </span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}

// ============================================
// 5. FAQ - 아코디언
// ============================================

interface FAQItem {
    question: string;
    answer: string;
}

interface FAQProps {
    title: string;
    items: FAQItem[];
}

export function FAQ({ title, items }: FAQProps) {
    const [openIndex, setOpenIndex] = useState<number | null>(0);

    return (
        <section className="py-24 bg-white">
            <div className="max-w-3xl mx-auto px-6">
                <h2 className="text-4xl font-bold text-slate-900 text-center mb-16">
                    {title}
                </h2>

                <div className="space-y-4">
                    {items.map((item, i) => (
                        <div key={i} className="border border-slate-200 rounded-lg overflow-hidden">
                            <button
                                onClick={() => setOpenIndex(openIndex === i ? null : i)}
                                className="w-full px-6 py-5 text-left flex items-center justify-between hover:bg-slate-50 transition-colors"
                            >
                                <span className="font-semibold text-slate-900 pr-4">
                                    {item.question}
                                </span>
                                <ChevronDown
                                    className={`w-5 h-5 text-slate-600 transition-transform flex-shrink-0 ${openIndex === i ? 'rotate-180' : ''
                                        }`}
                                />
                            </button>

                            <div
                                className={`overflow-hidden transition-all duration-200 ${openIndex === i ? 'max-h-96' : 'max-h-0'
                                    }`}
                            >
                                <div className="px-6 pb-5 text-slate-600 leading-relaxed">
                                    {item.answer}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}

// ============================================
// 6. FINAL CTA - 리스크 역전 포함
// ============================================

interface FinalCTAProps {
    title: string;
    subtitle: string;
    ctaText: string;
    riskReversals?: string[];
    onClick?: () => void;
}

export function FinalCTA({ title, subtitle, ctaText, riskReversals, onClick }: FinalCTAProps) {
    return (
        <section className="py-24 lg:py-32 bg-gradient-to-br from-blue-600 to-blue-700">
            <div className="max-w-4xl mx-auto px-6 text-center">
                <h2 className="text-4xl lg:text-5xl font-bold text-white mb-6">
                    {title}
                </h2>

                <p className="text-xl text-blue-100 mb-10">
                    {subtitle}
                </p>

                <button
                    onClick={onClick}
                    className="px-10 py-5 bg-white text-blue-600 text-lg font-semibold rounded-lg hover:bg-blue-50 transition-colors shadow-xl hover:shadow-2xl mb-6"
                >
                    {ctaText}
                </button>

                {riskReversals && riskReversals.length > 0 && (
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-6 text-sm text-blue-100">
                        {riskReversals.map((item, i) => (
                            <div key={i} className="flex items-center gap-2">
                                <Check className="w-5 h-5" />
                                {item}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </section>
    );
}

// ============================================
// 7. LOGO STRIP - 사회적 증거
// ============================================

interface LogoStripProps {
    title?: string;
    logoCount?: number;
}

export function LogoStrip({ title = "Trusted by leading companies", logoCount = 4 }: LogoStripProps) {
    return (
        <section className="py-16 bg-white border-y border-slate-200">
            <div className="max-w-7xl mx-auto px-6 lg:px-12">
                <p className="text-center text-sm font-semibold text-slate-600 mb-8 uppercase tracking-wider">
                    {title}
                </p>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-8 items-center justify-items-center">
                    {[...Array(logoCount)].map((_, i) => (
                        <div
                            key={i}
                            className="h-8 w-32 bg-slate-200 rounded opacity-50 grayscale hover:opacity-100 hover:grayscale-0 transition-all"
                        />
                    ))}
                </div>
            </div>
        </section>
    );
}

// ============================================
// 기본 내보내기
// ============================================

export default {
    HeroAsymmetric,
    Features,
    Testimonials,
    Pricing,
    FAQ,
    FinalCTA,
    LogoStrip
};
